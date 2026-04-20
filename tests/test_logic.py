import pytest
from django.db import models
import graphene
from tarxemo_django_graphene_utils.pagination import paginate_queryset, PageObject
from tarxemo_django_graphene_utils.filtering import apply_filters, BaseFilterInput

# Mock Model for testing
class MockModel(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'tests'

@pytest.mark.django_db
def test_paginate_queryset_basic():
    # We'd need to actually create objects if we want to test with real DB
    # or just mock the queryset
    from unittest.mock import MagicMock
    qs = [MagicMock() for _ in range(50)]
    paginator, page = paginate_queryset(qs, 1, 20)
    
    assert paginator.num_pages == 3
    assert page.number == 1
    assert len(page.object_list) == 20

def test_base_filter_input():
    # Just verify it has the right fields
    filters = BaseFilterInput()
    assert hasattr(filters, 'page_number')
    assert hasattr(filters, 'items_per_page')
    assert hasattr(filters, 'search_term')
