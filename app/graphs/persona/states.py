from pydantic import BaseModel, Field
from typing import TypedDict, Annotated
from operator import add

class PersonaSelection(BaseModel):
    persona_id: str = Field(
        description="The exact persona ID as it appears in the roster e.g. 'economist', 'lawyer', 'tech_analyst'"
    )
    reason: str = Field(
        description="One sentence explaining why this persona was selected for this specific story. Must reference something concrete in the article, not a generic domain match."
    )

class RouterOutput(BaseModel):
    personas: list[PersonaSelection] = Field(
        description="List of selected personas. Minimum 2, maximum 4. Does not include historian or anchor — they are assigned automatically."
    )
    anchor_needed: bool = Field(
        default=True,
        description="Whether the Anchor persona is needed. Almost always True. Set to False only for purely technical bulletins with no narrative framing required."
    )

class Personas(TypedDict):
    personas : Annotated[list[dict], add]