"""
Profile Pydantic schemas — request/response DTOs.
Separate from SQLAlchemy models to control API shape.
"""

from pydantic import BaseModel, EmailStr


class SkillResponse(BaseModel):
    id: str
    name: str
    category: str
    level: int

    model_config = {"from_attributes": True}


class ExperienceResponse(BaseModel):
    id: str
    company: str
    role: str
    description: str
    start_date: str
    end_date: str

    model_config = {"from_attributes": True}


class EducationResponse(BaseModel):
    id: str
    institution: str
    degree: str
    field: str
    start_date: str
    end_date: str

    model_config = {"from_attributes": True}


class ProfileResponse(BaseModel):
    id: str
    full_name: str
    headline: str
    summary: str
    email: str
    location: str
    github_url: str
    linkedin_url: str
    avatar_url: str
    skills: list[SkillResponse] = []
    experiences: list[ExperienceResponse] = []
    educations: list[EducationResponse] = []

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    headline: str | None = None
    summary: str | None = None
    email: str | None = None
    location: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    avatar_url: str | None = None


class CreateSkillRequest(BaseModel):
    name: str
    category: str
    level: int = 0


class SkillsGroupedResponse(BaseModel):
    category: str
    items: list[SkillResponse]
