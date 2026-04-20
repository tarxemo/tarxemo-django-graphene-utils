import graphene
from typing import Dict, Any, List, Optional, Union
from django.core.exceptions import ValidationError

class ErrorDetail(graphene.ObjectType):
    """Detailed error object for specific fields."""
    field = graphene.String()
    message = graphene.String()
    code = graphene.String()

def format_validation_error(error: Union[ValidationError, Dict[str, Any], str]) -> List[ErrorDetail]:
    """
    Standardizes various error formats into a list of ErrorDetail.
    Handles Django's ValidationError, dicts, and simple strings.
    """
    details = []
    
    if isinstance(error, ValidationError):
        if hasattr(error, 'message_dict'):
            for field, messages in error.message_dict.items():
                for msg in messages:
                    details.append(ErrorDetail(field=field, message=str(msg)))
        elif hasattr(error, 'messages'):
            for msg in error.messages:
                details.append(ErrorDetail(field=None, message=str(msg)))
                
    elif isinstance(error, dict):
        for field, message in error.items():
            details.append(ErrorDetail(field=field, message=str(message)))
            
    elif isinstance(error, str):
        details.append(ErrorDetail(field=None, message=error))
        
    return details
