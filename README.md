# TarXemo Django Graphene Utils

[![PyPI version](https://img.shields.io/pypi/v/tarxemo-django-graphene-utils.svg)](https://pypi.org/project/tarxemo-django-graphene-utils/)
[![Framework :: Django](https://img.shields.io/badge/framework-django-red.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Shared Django Graphene utilities and DTOs for efficient API development. This package provides standardized response builders, pagination helpers, and common GraphQL types.

## Installation

```bash
pip install tarxemo-django-graphene-utils
```

## Usage

### Standardized Responses

```python
from tarxemo_django_graphene_utils import build_success_response, build_error

def resolve_something(root, info):
    if success:
        return build_success_response("Operation successful")
    return build_error("Something went wrong")
```

### Pagination

```python
from tarxemo_django_graphene_utils import get_paginated_and_non_paginated_data

def resolve_items(root, info, **kwargs):
    return get_paginated_and_non_paginated_data(
        model=MyModel,
        filtering_object=kwargs,
        graphene_type=MyModelType
    )
```

## Building and Publishing

1. Build the package:
   ```bash
   python setup.py sdist bdist_wheel
   ```

2. Upload to PyPI (requires twine):
   ```bash
   twine upload dist/*
   ```
# tarxemo-django-graphene-utils
