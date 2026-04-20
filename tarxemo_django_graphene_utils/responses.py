from typing import Optional, Dict, Any, List, Union
import graphene
from .config import TarxemoConfig
from .validation import ErrorDetail
from .pagination import PageObject


class ResponseObject(graphene.ObjectType):
    """Standardized response metadata."""
    id = graphene.Int()
    status = graphene.Boolean()
    code = graphene.Int()
    message = graphene.String()
    errors = graphene.List(ErrorDetail)

class BaseResponseDTO(graphene.ObjectType):
    """Base DTO with standard response and optional paging.
    Inherit this and define/override the `data` field with the specific Graphene type.
    """
    response = graphene.Field(ResponseObject, required=True)
    page = graphene.Field(PageObject)

class ResponseRegistry:
    """Registry for response codes and messages."""
    
    @classmethod
    def get_response_data(cls, response_id: int) -> Dict[str, Any]:
        codes = TarxemoConfig.get('RESPONSE_CODES')
        return codes.get(response_id, codes[3])

def build_success_response(message: Optional[str] = None) -> ResponseObject:
    res = ResponseRegistry.get_response_data(1)
    return ResponseObject(
        id=res["id"],
        status=res["status"],
        code=res["code"],
        message=message if message else TarxemoConfig.get('DEFAULT_SUCCESS_MESSAGE')
    )

def build_no_results_response(message: Optional[str] = None) -> ResponseObject:
    res = ResponseRegistry.get_response_data(0)
    return ResponseObject(
        id=res["id"],
        status=res["status"],
        code=res["code"],
        message=message if message else res["message"]
    )

def build_error_response(message: Optional[str] = None, code: Optional[int] = None) -> ResponseObject:
    res = ResponseRegistry.get_response_data(3)
    return ResponseObject(
        id=res["id"],
        status=res["status"],
        code=code if code is not None else res["code"],
        message=message if message else TarxemoConfig.get('DEFAULT_ERROR_MESSAGE')
    )

def build_error(message: str, code: Optional[int] = None) -> ResponseObject:
    """Shortcut for build_error_response."""
    return build_error_response(message=message, code=code)
