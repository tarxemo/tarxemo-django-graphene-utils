import operator
from functools import reduce
from typing import Dict, Any, Optional, Type, List
from django.db.models import Model, Q, QuerySet, CharField, TextField, BooleanField
import graphene

class BaseFilterInput(graphene.InputObjectType):
    """Base GraphQL input for filtering and pagination."""
    page_number = graphene.Int()
    items_per_page = graphene.Int()
    search_term = graphene.String()
    is_paged = graphene.Boolean(default_value=True)
    is_active = graphene.Boolean()
    order_by = graphene.String()

def apply_search_filter(queryset: QuerySet, model: Type[Model], search_term: str) -> QuerySet:
    """Dynamically applies a search filter across all Char and Text fields."""
    query_to_search = {}
    for field in model._meta.get_fields():
        if isinstance(field, (CharField, TextField)):
            query_to_search[field.name + "__icontains"] = search_term

    if not query_to_search:
        return queryset

    return queryset.filter(
        reduce(
            operator.or_, (Q(**{k: v}) for k, v in query_to_search.items())
        )
    )

def apply_filters(
    queryset: QuerySet,
    model: Type[Model],
    filter_dict: Dict[str, Any],
    custom_look_up: Optional[Dict[str, str]] = None
) -> QuerySet:
    """
    Applies filters to a queryset based on a dictionary.
    Handles 'is_active' automatically if the model has the field.
    """
    filters = filter_dict.copy()
    
    # Remove pagination/search from filter dict
    filters.pop("page_number", None)
    filters.pop("pageNumber", None)
    filters.pop("items_per_page", None)
    filters.pop("itemsPerPage", None)
    filters.pop("is_paged", None)
    filters.pop("isPaged", None)
    
    search_term = filters.pop("search_term", filters.pop("searchTerm", None))
    order_by = filters.pop("order_by", filters.pop("orderBy", None))

    # Apply custom lookups
    if custom_look_up:
        for key, lookup in custom_look_up.items():
            if key in filters:
                filters[lookup] = filters.pop(key)

    # Smart auto-lookups based on field types
    final_filters = {}
    model_fields = {f.name: f for f in model._meta.get_fields()}

    for key, value in filters.items():
        if value is None:
            continue
            
        base_key = key.split('__')[0]
        if base_key in model_fields:
            field = model_fields[base_key]
            # If the user didn't specify a lookup, maybe add one
            if '__' not in key:
                if isinstance(field, BooleanField):
                    final_filters[key] = bool(value)
                    continue
                # Dates and UUIDs often benefit from exact or specialized lookups
                # but we'll stick to basic exact if not specified for now
        
        final_filters[key] = value

    # Handle is_active default behavior
    if "is_active" not in final_filters:
        has_is_active = "is_active" in model_fields
        if has_is_active:
             final_filters["is_active"] = True
    elif final_filters["is_active"] is None:
        final_filters.pop("is_active")

    queryset = queryset.filter(**final_filters)

    if search_term:
        queryset = apply_search_filter(queryset, model, search_term)
        
    if order_by:
        # Prevent SQL injection or invalid field sorting
        direction = ""
        if order_by.startswith("-"):
            direction = "-"
            order_by = order_by[1:]
        
        # Verify field exists before ordering
        if order_by in model_fields:
            queryset = queryset.order_by(f"{direction}{order_by}")

    return queryset
