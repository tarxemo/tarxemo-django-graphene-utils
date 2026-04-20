import graphene
from typing import Any, Tuple, Optional
from django.core.paginator import Paginator
from django.db.models import QuerySet

class PageObject(graphene.ObjectType):
    """Standard Graphene object for pagination info."""
    number = graphene.Int()
    has_next_page = graphene.Boolean()
    has_previous_page = graphene.Boolean()
    current_page_number = graphene.Int()
    next_page_number = graphene.Int()
    previous_page_number = graphene.Int()
    number_of_pages = graphene.Int()
    total_elements = graphene.Int()
    pages_number_array = graphene.List(graphene.Int)


def paginate_queryset(queryset: QuerySet, page_number: int, items_per_page: int) -> Tuple[Paginator, Any]:
    """Helper to paginate a Django queryset."""
    paginator = Paginator(queryset, items_per_page)
    if page_number > paginator.num_pages or page_number < 1:
        return paginator, None
    return paginator, paginator.page(page_number)
