"""Core schemas module"""

from pydantic import BaseModel, ConfigDict

from core.utils.parses import to_camel_case


class CamelBaseModel(BaseModel):
    """Base model that exposes camelCase fields in API payloads."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel_case,
        extra="ignore",
    )
