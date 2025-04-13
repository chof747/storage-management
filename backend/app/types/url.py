# types/urls.py

import re
from pydantic_core import PydanticCustomError
from pydantic import GetCoreSchemaHandler
from typing import Any
from pydantic_core.core_schema import CoreSchema, no_info_plain_validator_function

URL_REGEX = re.compile(
    r'^(https?):\/\/'                  # http:// or https://
    r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,})'  # domain
    r'(:\d+)?'                          # optional port
    r'(\/\S*)?$',                       # optional path
    re.IGNORECASE
)

class StrHttpUrl(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> CoreSchema:
        return no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("String required")
        if not URL_REGEX.match(value):
            raise PydanticCustomError("url_format", "Invalid URL format (must be http/https and valid domain)")
        return value
