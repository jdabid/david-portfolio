"""
UpdateProfile command — CQRS write side.
Validates, persists changes to PostgreSQL, and invalidates Redis cache.
"""

from dataclasses import dataclass

from sqlalchemy import select

from app.infrastructure.cache import cache_delete
from app.infrastructure.database import async_session
from app.features.profile.models import Profile
from app.shared.mediator import Command, register_command_handler


@dataclass(frozen=True)
class UpdateProfileCommand(Command):
    profile_id: str
    data: dict


async def handle_update_profile(command: UpdateProfileCommand) -> dict:
    async with async_session() as session:
        result = await session.execute(
            select(Profile).where(Profile.id == command.profile_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise ValueError(f"Profile {command.profile_id} not found")

        for key, value in command.data.items():
            if value is not None and hasattr(profile, key):
                setattr(profile, key, value)

        await session.commit()
        await session.refresh(profile)

        # Invalidate cache
        await cache_delete("profile:*")

        return {"id": str(profile.id), "full_name": profile.full_name}


register_command_handler(UpdateProfileCommand, handle_update_profile)
