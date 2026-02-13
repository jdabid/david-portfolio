"""
Project Pydantic schemas.
"""

from pydantic import BaseModel


class ProjectResponse(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    long_description: str
    tags: list[str]
    image_url: str
    github_url: str
    live_url: str
    featured: bool

    model_config = {"from_attributes": True}


class ProjectListItem(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    tags: list[str]
    image_url: str
    featured: bool

    model_config = {"from_attributes": True}


class CreateProjectRequest(BaseModel):
    title: str
    slug: str
    description: str
    long_description: str = ""
    tags: list[str] = []
    image_url: str = ""
    github_url: str = ""
    live_url: str = ""
    featured: bool = False
    sort_order: int = 0
