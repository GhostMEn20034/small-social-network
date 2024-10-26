from typing import Optional

from pydantic import BaseModel, conint, field_validator
from pydantic_core.core_schema import ValidationInfo


class PostCreateSchema(BaseModel):
    title: str
    content: str
    draft: bool = False
    auto_reply: bool = False
    reply_after: Optional[conint(gt=0)] = None

    @field_validator('reply_after')
    def auto_reply_functionality_setup_correctly(cls, value, info: ValidationInfo):
        """Ensure that if auto_reply is set to True, reply_after is not None and it's integer"""
        auto_reply = info.data["auto_reply"]
        if auto_reply and not isinstance(value, int):
            raise ValueError('If you want to enable auto reply feature, you also must set reply after field')

        return value
