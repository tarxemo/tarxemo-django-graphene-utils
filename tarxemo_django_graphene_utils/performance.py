from typing import List, Optional, Type, Union
from django.db.models import QuerySet, Model, ForeignKey, OneToOneField, ManyToManyField, Field

def auto_optimize(
    queryset: QuerySet,
    requested_fields: List[str],
    model: Optional[Type[Model]] = None
) -> QuerySet:
    """
    Automatically applies select_related and prefetch_related to a queryset
    based on a list of requested fields. Useful for N+1 prevention.
    """
    if not model:
        model = queryset.model
        
    select_fields = []
    prefetch_fields = []
    
    model_fields = {f.name: f for f in model._meta.get_fields()}
    
    for field_name in requested_fields:
        # Handle nested fields (e.g., 'author__profile')
        base_field = field_name.split('__')[0]
        
        if base_field in model_fields:
            field = model_fields[base_field]
            
            if isinstance(field, (ForeignKey, OneToOneField)):
                select_fields.append(field_name)
            elif isinstance(field, (ManyToManyField, Field)) and hasattr(field, 'related_model'):
                # Covers Reverse ForeignKeys and ManyToMany
                prefetch_fields.append(field_name)

    if select_fields:
        queryset = queryset.select_related(*select_fields)
    if prefetch_fields:
        queryset = queryset.prefetch_related(*prefetch_fields)
        
    return queryset
