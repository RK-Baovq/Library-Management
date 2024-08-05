from pydantic import BaseModel


class CategoryIn(BaseModel):
    name: str
