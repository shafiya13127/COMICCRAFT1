from typing import List

from pydantic import BaseModel, Field, field_validator


class ComicRequest(BaseModel):

    prompt: str = Field(
        ...,
        min_length=3,
        max_length=2000
    )

    style: str = Field(
        default="Adventure",
        max_length=50
    )

    language: str = Field(
        default="English",
        max_length=30
    )

    panels: int = Field(
        default=5,
        ge=3,
        le=8
    )

    @field_validator("prompt")
    @classmethod
    def clean_prompt(cls, value: str) -> str:
        return " ".join(value.strip().split())


class Panel(BaseModel):

    panel: int

    title: str

    scene_description: str

    narration: str

    dialogue: List[str] = Field(
        default_factory=list
    )


class ComicResponse(BaseModel):

    title: str

    characters: List[str]

    panels: List[Panel]

    style: str

    language: str