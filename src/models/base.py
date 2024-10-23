from sqlmodel import SQLModel, Field, Column, Integer

from src.utils.str_utils import to_camel_case


class BaseModel(SQLModel):
    """Base SQL model class.
    """

    id: int | None = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True))

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        arbitrary_types_allowed = True