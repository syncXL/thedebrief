from pydantic import BaseModel, Field

class SelectedArticles(BaseModel):
    indices: list[int] = Field(
        ...,
        max_length=5,
        description="Indexes of the top 5 selected articles. Maximum 5."
    )