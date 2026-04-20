# TarXemo Django Graphene Utils

**Professional, modular, and high-performance GraphQL utilities for Django.**

This package provides a standardized toolkit to accelerate GraphQL API development. It handles the "boring" parts—pagination, filtering, response standardization, and N+1 prevention—so you can focus on building features.

---

## ✨ Features

- **🚀 Performance-First**: Internal field caching and `auto_optimize` helper for N+1 query prevention.
- **🛠 Modular & Flexible**: Clean separation between responses, pagination, and filtering.
- **🧠 Smart & Forgiving**: Automatically handles both `camelCase` and `snake_case` inputs.
- **✅ Structured Validation**: Integrated support for Django `ValidationError` with standardized field-level error reporting.
- **⚙️ Fully Configurable**: Global settings support via Django `settings.py`.

---

## 📦 Installation

```bash
pip install tarxemo-django-graphene-utils
```

---

## 📖 Full Usage Guide

### 1. Standardized Responses

Every API should speak the same language. Use these builders to return consistent metadata to your frontend.

```python
from tarxemo_django_graphene_utils import build_success_response, build_error, build_validation_error

def resolve_my_mutation(root, info, input):
    try:
        # Business logic here...
        return build_success_response("Item created successfully")
    except ValidationError as e:
        # Standardized field-level errors: {"field": "email", "message": "Invalid format"}
        return build_validation_error(e)
    except Exception as e:
        return build_error(str(e), code=9003)
```

### 2. High-Performance Data Retrieval

The core utility `get_paginated_and_non_paginated_data` handles everything from filtering to pagination in one call.

```python
from tarxemo_django_graphene_utils import get_paginated_and_non_paginated_data, BaseFilterInput
import graphene

class MyFilter(BaseFilterInput):
    # Inherits: page_number, items_per_page, search_term, is_paged, is_active, order_by
    category = graphene.String()

def resolve_items(root, info, **kwargs):
    return get_paginated_and_non_paginated_data(
        model_or_queryset=MyModel, # Can also be MyModel.objects.select_related(...)
        filtering_object=kwargs,
        graphene_type=MyModelGrapheneType
    )
```

### 3. N+1 Prevention with `auto_optimize`

Prevent database bottlenecks by automatically applying `select_related` and `prefetch_related` based on requested fields.

```python
from tarxemo_django_graphene_utils import auto_optimize

def resolve_list(root, info, **kwargs):
    # Determine requested fields from info or custom list
    requested = ['author', 'author__profile', 'tags']
    
    qs = MyModel.objects.all()
    optimized_qs = auto_optimize(qs, requested)
    
    return build_paged_list(optimized_qs, MyType, **kwargs)
```

### 4. Robust Object Mapping

Convert Django Models or Dicts to Graphene types with high-performance caching.

```python
from tarxemo_django_graphene_utils import to_graphene

# Caches field discovery internally—extremely fast for large lists!
graph_obj = to_graphene(model_instance, MyGrapheneType)
```

### 5. Common GraphQL Types

Save time by using pre-defined common types:
- `BaseType`: Includes `id` (UUID), `created_at`, `updated_at`, `is_active`.
- `LocationInput`: `latitude`, `longitude`, `radius`.
- `DateRangeInput`: `start_date`, `end_date`.
- `SortInput`: `field`, `reverse`.

---

## ⚙️ Configuration

Customize the library behavior in your Django `settings.py`:

```python
TARXEMO_UTILS_CONFIG = {
    'ITEMS_PER_PAGE': 50,
    'DEFAULT_SUCCESS_MESSAGE': "Done!",
    'DEFAULT_ERROR_MESSAGE': "Oops, something broke.",
    'RESPONSE_CODES': {
        2001: {"id": 2001, "status": True, "code": 700, "message": "Custom Event"},
    }
}
```

---

## 🧪 Development

1. **Install for development**:
   ```bash
   pip install -e ".[dev]"
   ```

2. **Run Tests**:
   ```bash
   pytest
   ```

## 📄 License

MIT © [TarXemo](https://github.com/tarxemo)
