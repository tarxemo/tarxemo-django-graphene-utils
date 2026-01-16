import json
import operator
import os
from pathlib import Path
from typing import Type, TypeVar, Optional, Dict, Any, Iterable, Callable, List, Tuple
from django.core.paginator import Paginator
from django.db.models import Model, Q, QuerySet, CharField, TextField
from functools import reduce
import graphene
from django.conf import settings
from graphene import InputObjectType

T = TypeVar("T", bound=Model)

# ------------------------------
# Filters
# ------------------------------

class UserFilterInput(InputObjectType):
    page_number = graphene.Int()
    items_per_page = graphene.Int()
    search_term = graphene.String()
    user_type = graphene.String()
    verification_status = graphene.String()
    city = graphene.String()
    country = graphene.String()
    is_paged = graphene.Boolean()
    
    # Task specific filters (Consider moving to specific implementations if too specific)
    store_id = graphene.UUID() 

class ResponseObject(graphene.ObjectType):
    id = graphene.Int()
    status = graphene.Boolean()
    code = graphene.Int()
    message = graphene.String()

    @staticmethod
    def _read_code_file(code_id: int) -> dict:
        candidates: List[Path] = []
        try:
            base_dir = Path(getattr(settings, 'BASE_DIR', Path.cwd()))
            candidates.append(base_dir / 'ecommerce_assets' / 'responses.json')
        except Exception:
            pass

        candidates.append(Path.cwd() / 'responses.json')
        # Look in the package directory itself if distributed with one
        candidates.append(Path(__file__).resolve().parent / 'responses.json')

        data: Optional[List[Dict[str, Any]]] = None
        for p in candidates:
            try:
                if p.exists():
                    with p.open('r', encoding='utf-8') as f:
                        data = json.load(f)
                        break
            except Exception:
                continue

        if not data:
            data = [
                {"id": 0, "status": False, "code": 9000, "message": "No results"},
                {"id": 1, "status": True, "code": 2000, "message": "Success"},
                {"id": 2, "status": False, "code": 9002, "message": "Validation error"},
                {"id": 3, "status": False, "code": 9003, "message": "Unexpected error"},
            ]

        return next((code for code in data if code.get("id") == code_id), data[1])

    @classmethod
    def get_response(cls, id: int, message: Optional[str] = None):
        response_code = cls._read_code_file(id)
        return cls(
            id=response_code["id"],
            status=response_code["status"],
            code=response_code["code"],
            message=message if message else response_code["message"],
        )
    
class PageObject(graphene.ObjectType):
    number = graphene.Int()
    has_next_page = graphene.Boolean()
    has_previous_page = graphene.Boolean()
    current_page_number = graphene.Int()
    next_page_number = graphene.Int()
    previous_page_number = graphene.Int()
    number_of_pages = graphene.Int()
    total_elements = graphene.Int()
    pages_number_array = graphene.List(graphene.Int)


# ------------------------------
# Base DTOs to inherit
# ------------------------------

class BaseResponseDTO(graphene.ObjectType):
    """Base DTO with standard response and optional paging.
    Inherit this and define/override the `data` field with the specific Graphene type.
    """
    response = graphene.Field(ResponseObject, required=True)
    page = graphene.Field(PageObject)


# ------------------------------
# Utilities
# ------------------------------

def apply_search_filter(queryset: QuerySet, model: Model, search_term: str):
    query_to_search = {}
    for field in model._meta.get_fields():
        if isinstance(field, (CharField, TextField)):
            query_to_search[field.name + "__icontains"] = search_term

    return queryset.filter(
        reduce(
            operator.or_, (Q(**{k: v}) for k, v in query_to_search.items())
        )
    )


def _to_graphene(obj: Model, graphene_type: graphene.ObjectType):
    """Safely map a Django model instance to a Graphene ObjectType instance."""
    try:
        field_names = []
        meta = getattr(graphene_type, '_meta', None)
        if meta and hasattr(meta, 'fields') and meta.fields:
            try:
                field_names = list(meta.fields.keys())
            except Exception:
                field_names = [getattr(f, 'name', None) for f in meta.fields] 
        kwargs = {}
        for name in field_names:
            if not name:
                continue
            if hasattr(obj, name):
                value = getattr(obj, name)
                kwargs[name] = value
        if not kwargs:
            kwargs = {k: v for k, v in vars(obj).items() if not k.startswith('_')}
        return graphene_type(**kwargs)
    except Exception:
        return graphene_type(**{k: v for k, v in vars(obj).items() if not k.startswith('_')})


def _paginate_queryset(queryset: QuerySet, page_number: int, items_per_page: int) -> Tuple[Paginator, Any]:
    paginator = Paginator(queryset, items_per_page)
    if page_number > paginator.num_pages or page_number < 1:
        return paginator, None
    return paginator, paginator.page(page_number)


def build_success_response(message: Optional[str] = None) -> ResponseObject:
    return ResponseObject.get_response(1, message=message)


def build_no_results_response(message: Optional[str] = None) -> ResponseObject:
    return ResponseObject.get_response(0, message=message or "No results")


def build_error_response(message: Optional[str] = None) -> ResponseObject:
    return ResponseObject.get_response(3, message=message or "Unexpected error")


def get_paginated_and_non_paginated_data(
    model: Type[T],
    filtering_object: Dict[str, Any],
    graphene_type: graphene.ObjectType,
    additional_filters: Optional[Q] = None,
    custom_look_up_filter: Optional[Dict[str, str]] = None,
    is_paged: bool = True,
):
    try:
        if custom_look_up_filter is None:
            custom_look_up_filter = {}

        filter_dict = dict(filtering_object)

        if is_paged:
            filter_dict.pop("pageNumber", None)
            filter_dict.pop("itemsPerPage", None)

        search_term = filter_dict.pop("searchTerm", None)

        for attr, value in list(filter_dict.items()):
            if value is None:
                filter_dict.pop(attr)
            elif custom_look_up_filter.get(attr):
                filter_dict[custom_look_up_filter[attr]] = value
                filter_dict.pop(attr)

        if filter_dict.get("is_active", None) is None:
            # Check if model has is_active field before filtering
            if hasattr(model, 'is_active') or any(f.name == 'is_active' for f in model._meta.get_fields()):
                 filter_dict["is_active"] = True
            else:
                 filter_dict.pop("is_active", None)

        queryset = model.objects.filter(**filter_dict)
        if additional_filters:
            queryset = queryset.filter(additional_filters)

        if search_term:
            queryset = apply_search_filter(queryset, model, search_term)

        if not is_paged:
            return {
                "response": build_success_response(),
                "data": [_to_graphene(obj, graphene_type) for obj in queryset],
            }

        raw_page = filtering_object.get("pageNumber")
        raw_per_page = filtering_object.get("itemsPerPage")
        try:
            page_number = int(raw_page) if raw_page is not None else 1
        except Exception:
            page_number = 1
        try:
            items_per_page = int(raw_per_page) if raw_per_page is not None else 20
        except Exception:
            items_per_page = 20

        paginator, page_obj = _paginate_queryset(queryset, page_number, items_per_page)

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
            current_page_number=page_number,
            next_page_number=page_obj.next_page_number() if page_obj.has_next() else None,
            previous_page_number=page_obj.previous_page_number() if page_obj.has_previous() else None,
            number_of_pages=paginator.num_pages,
            total_elements=paginator.count,
            pages_number_array=list(range(1, paginator.num_pages + 1)),
        )

        return {
            "response": build_success_response(),
            "page": page_info,
            "data": [_to_graphene(obj, graphene_type) for obj in page_obj.object_list],
        }

    except Exception as e:
        return {
            "response": build_error_response(message=str(e)),
            "page": None,
            "data": [],
        }


def build_non_paged_list(
    objects: Iterable[Model],
    graphene_type: graphene.ObjectType,
    message: Optional[str] = None,
):
    return {
        "response": build_success_response(message=message),
        "data": [_to_graphene(obj, graphene_type) for obj in objects],
    }


def build_single_object(
    obj: Optional[Model],
    graphene_type: graphene.ObjectType,
    not_found_message: str = "Not found",
    message: Optional[str] = None,
):
    if obj is None:
        return {
            "response": build_no_results_response(message=not_found_message),
            "data": None,
        }
    return {
        "response": build_success_response(message=message),
        "data": _to_graphene(obj, graphene_type),
    }


def build_paged_list(
    queryset: QuerySet,
    graphene_type: graphene.ObjectType,
    page_number: int = 1,
    items_per_page: int = 20,
    message: Optional[str] = None,
):
    try:
        page_number = int(page_number) if page_number is not None else 1
    except Exception:
        page_number = 1
    try:
        items_per_page = int(items_per_page) if items_per_page is not None else 20
    except Exception:
        items_per_page = 20

    paginator, page_obj = _paginate_queryset(queryset, page_number, items_per_page)
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
        current_page_number=page_number,
        next_page_number=page_obj.next_page_number() if page_obj.has_next() else None,
        previous_page_number=page_obj.previous_page_number() if page_obj.has_previous() else None,
        number_of_pages=paginator.num_pages,
        total_elements=paginator.count,
        pages_number_array=list(range(1, paginator.num_pages + 1)),
    )

    return {
        "response": build_success_response(message=message),
        "page": page_info,
        "data": [_to_graphene(obj, graphene_type) for obj in page_obj.object_list],
    }


def build_error(message: str):
    return build_error_response(message=message)
