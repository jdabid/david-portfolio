"""
GetProfile query — CQRS read side.
Reads from Redis cache first, falls back to PostgreSQL.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.infrastructure.cache import cache_get, cache_set
from app.infrastructure.database import async_session
from app.features.profile.models import Profile
from app.shared.mediator import Query, register_query_handler

CACHE_KEY = "profile:main"
CACHE_TTL = 600  # 10 minutes


@dataclass(frozen=True)
class GetProfileQuery(Query):
    pass


async def handle_get_profile(query: GetProfileQuery) -> dict | None:
    # Check cache first
    cached = await cache_get(CACHE_KEY)
    if cached:
        return cached

    # Fallback to database
    async with async_session() as session:
        result = await session.execute(
            select(Profile)
            .options(
                selectinload(Profile.skills),
                selectinload(Profile.experiences),
                selectinload(Profile.educations),
            )
            .limit(1)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            return None

        data = {
            "id": str(profile.id),
            "full_name": profile.full_name,
            "headline": profile.headline,
            "summary": profile.summary,
            "email": profile.email,
            "location": profile.location,
            "github_url": profile.github_url,
            "linkedin_url": profile.linkedin_url,
            "avatar_url": profile.avatar_url,
            "skills": [
                {
                    "id": str(s.id),
                    "name": s.name,
                    "category": s.category,
                    "level": s.level,
                }
                for s in profile.skills
            ],
            "experiences": [
                {
                    "id": str(e.id),
                    "company": e.company,
                    "role": e.role,
                    "description": e.description,
                    "start_date": e.start_date,
                    "end_date": e.end_date,
                }
                for e in sorted(profile.experiences, key=lambda x: x.start_date, reverse=True)
            ],
            "educations": [
                {
                    "id": str(ed.id),
                    "institution": ed.institution,
                    "degree": ed.degree,
                    "field": ed.field,
                    "start_date": ed.start_date,
                    "end_date": ed.end_date,
                }
                for ed in profile.educations
            ],
        }

        # Store in cache
        await cache_set(CACHE_KEY, data, CACHE_TTL)
        return data


register_query_handler(GetProfileQuery, handle_get_profile)
