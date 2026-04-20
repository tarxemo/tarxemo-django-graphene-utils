from functools import lru_cache
from typing import Type, TypeVar, Optional, Dict, Any, Iterable, List, Union
from django.db.models import Model, Q, QuerySet
import graphene

from .pagination import PageObject, paginate_queryset
from .responses import (
    ResponseObject, 
    BaseResponseDTO, 
    build_success_response, 
    build_no_results_response, 
    build_error_response,
    build_error
)
from .filtering import apply_filters, BaseFilterInput
from .config import TarxemoConfig
from .validation import format_validation_error

T = TypeVar("T", bound=Model)

@lru_cache(maxsize=128)
def _get_type_fields(graphene_type: Type[graphene.ObjectType]) -> List[str]:
    """Internal helper to cache field discovery for Graphene types."""
    meta = getattr(graphene_type, '_meta', None)
    if meta and hasattr(meta, 'fields'):
        return list(meta.fields.keys())
    return [attr for attr in dir(graphene_type) if not attr.startswith('_')]

def to_graphene(obj: Any, graphene_type: Type[graphene.ObjectType]) -> Optional[graphene.ObjectType]:
    """
    Robustly map a Django model instance (or dict/object) to a Graphene ObjectType.
    High-performance version with field caching.
    """
    if obj is None:
        return None
    
    if isinstance(obj, graphene_type):
        return obj

    kwargs = {}
    field_names = _get_type_fields(graphene_type)

    for name in field_names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if callable(value) and not isinstance(value, Model):
                try:
                    value = value()
                except Exception:
                    pass
            kwargs[name] = value
        elif isinstance(obj, dict) and name in obj:
            kwargs[name] = obj[name]

    return graphene_type(**kwargs)

def build_single_object(
    obj: Optional[Model],
    graphene_type: Type[graphene.ObjectType],
    not_found_message: str = "Not found",
    message: Optional[str] = None,
) -> Dict[str, Any]:
    """Helper to build a response for a single object. Accepting Model or None."""
    if obj is None:
        return {
            "response": build_no_results_response(message=not_found_message),
            "data": None,
        }
    return {
        "response": build_success_response(message=message),
        "data": to_graphene(obj, graphene_type),
    }

def build_paged_list(
    queryset: QuerySet,
    graphene_type: Type[graphene.ObjectType],
    page_number: Any = 1,
    items_per_page: Any = None,
    message: Optional[str] = None,
) -> Dict[str, Any]:
    """Helper to build a paginated response. Smart input handling for numbers."""
    default_per_page = TarxemoConfig.get('ITEMS_PER_PAGE')
    
    try:
        page_num = int(page_number) if page_number is not None else 1
    except (ValueError, TypeError):
        page_num = 1
        
    try:
        per_page = int(items_per_page) if items_per_page is not None else default_per_page
    except (ValueError, TypeError):
        per_page = default_per_page

    paginator, page_obj = paginate_queryset(queryset, page_num, per_page)
    
    if page_obj is None:
        return {
            "response": build_no_results_response(message="This page has no results"),
            "page": None,
            "data": [],
        }

    page_info = PageObject(
        number=page_obj.number,
        has_next_page=page_obj.has_next(),
        has_previous_page=page_obj.has_previous(),
        current_page_number=page_num,
        next_page_number=page_obj.next_page_number() if page_obj.has_next() else None,
        previous_page_number=page_obj.previous_page_number() if page_obj.has_previous() else None,
        number_of_pages=paginator.num_pages,
        total_elements=paginator.count,
        pages_number_array=list(range(1, paginator.num_pages + 1)),
    )

    return {
        "response": build_success_response(message=message),
        "page": page_info,
        "data": [to_graphene(obj, graphene_type) for obj in page_obj.object_list],
    }

def build_validation_error(error: Any, message: Optional[str] = None) -> Dict[str, Any]:
    """Helper to build a standardized validation error response."""
    response = build_error_response(
        id=2, 
        message=message or TarxemoConfig.get('RESPONSE_CODES')[2]['message']
    )
    response.errors = format_validation_error(error)
    return {"response": response, "data": None}

def get_paginated_and_non_paginated_data(
    model_or_queryset: Union[Type[T], QuerySet],
    filtering_object: Any,
    graphene_type: Type[graphene.ObjectType],
    additional_filters: Optional[Q] = None,
    custom_look_up_filter: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    High-level utility to filter and optionally paginate data.
    Supports both Model classes and pre-optimized QuerySets.
    Smartly handles both camelCase and snake_case inputs.
    """
    try:
        # Forgiving input handling
        if hasattr(filtering_object, 'items'):
            filter_dict = {k: v for k, v in filtering_object.items()}
        elif hasattr(filtering_object, '__dict__') and not isinstance(filtering_object, dict):
             filter_dict = vars(filtering_object)
        else:
            filter_dict = dict(filtering_object)

        # Allow user to pass a pre-built queryset or a model
        if isinstance(model_or_queryset, QuerySet):
            queryset = model_or_queryset
            model = model_or_queryset.model
        else:
            queryset = model_or_queryset.objects.all()
            model = model_or_queryset

        is_paged = filter_dict.get("is_paged", filter_dict.get("isPaged", True))
        
        if additional_filters:
            queryset = queryset.filter(additional_filters)
            
        queryset = apply_filters(queryset, model, filter_dict, custom_look_up=custom_look_up_filter)

        if not is_paged:
            return {
                "response": build_success_response(),
                "data": [to_graphene(obj, graphene_type) for obj in queryset],
            }

        page_number = filter_dict.get("page_number", filter_dict.get("pageNumber", 1))
        items_per_page = filter_dict.get("items_per_page", filter_dict.get("itemsPerPage"))

        return build_paged_list(
            queryset=queryset,
            graphene_type=graphene_type,
            page_number=page_number,
            items_per_page=items_per_page
        )

    except Exception as e:
        return {
            "response": build_error_response(message=str(e)),
            "page": None,
            "data": [],
        }

# For backward compatibility
_to_graphene = to_graphene
UserFilterInput = BaseFilterInput
