"""
Profile API endpoints — thin layer that delegates to CQRS handlers.
"""

from fastapi import APIRouter, HTTPException

from app.features.profile.schemas import ProfileResponse, UpdateProfileRequest
from app.features.profile.commands.update_profile import UpdateProfileCommand
from app.features.profile.queries.get_profile import GetProfileQuery
from app.features.profile.queries.get_skills import GetSkillsQuery
from app.shared.mediator import send_command, send_query

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
async def get_profile():
    """Get the main profile with skills, experience, and education."""
    result = await send_query(GetProfileQuery())
    if not result:
        raise HTTPException(status_code=404, detail="Profile not found")
    return result


@router.get("/skills")
async def get_skills():
    """Get skills grouped by category."""
    return await send_query(GetSkillsQuery())


@router.patch("/{profile_id}")
async def update_profile(profile_id: str, body: UpdateProfileRequest):
    """Update profile fields (partial update)."""
    data = body.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    return await send_command(UpdateProfileCommand(profile_id=profile_id, data=data))
