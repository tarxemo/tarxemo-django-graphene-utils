from django.conf import settings
from typing import Any, Dict

class TarxemoConfig:
    """Central configuration for the library."""
    
    DEFAULTS = {
        'ITEMS_PER_PAGE': 20,
        'DEFAULT_SUCCESS_MESSAGE': "Operation successful",
        'DEFAULT_ERROR_MESSAGE': "Unexpected error",
        'AUTO_CONVERT_CAMEL_CASE': True,
        'RESPONSE_CODES': {
            0: {"id": 0, "status": False, "code": 9000, "message": "No results"},
            1: {"id": 1, "status": True, "code": 2000, "message": "Success"},
            2: {"id": 2, "status": False, "code": 9002, "message": "Validation error"},
            3: {"id": 3, "status": False, "code": 9003, "message": "Unexpected error"},
            4: {"id": 4, "status": False, "code": 4001, "message": "Unauthorized"},
            5: {"id": 5, "status": False, "code": 4003, "message": "Forbidden"},
            6: {"id": 6, "status": False, "code": 4004, "message": "Not found"},
        }
    }

    @classmethod
    def get(cls, key: str) -> Any:
        user_config = getattr(settings, 'TARXEMO_UTILS_CONFIG', {})
        # Special handling for RESPONSE_CODES to merge instead of overwrite
        if key == 'RESPONSE_CODES':
            base = cls.DEFAULTS['RESPONSE_CODES'].copy()
            base.update(user_config.get('RESPONSE_CODES', {}))
            return base
            
        return user_config.get(key, cls.DEFAULTS.get(key))
