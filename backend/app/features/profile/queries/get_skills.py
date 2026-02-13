"""
GetSkills query — returns skills grouped by category.
Uses Redis cache with cache-aside pattern.
"""

from dataclasses import dataclass
from itertools import groupby
from operator import attrgetter

from sqlalchemy import select

from app.infrastructure.cache import cache_get, cache_set
from app.infrastructure.database import async_session
from app.features.profile.models import Skill
from app.shared.mediator import Query, register_query_handler

CACHE_KEY = "profile:skills"
CACHE_TTL = 600


@dataclass(frozen=True)
class GetSkillsQuery(Query):
    pass


async def handle_get_skills(query: GetSkillsQuery) -> list[dict]:
    cached = await cache_get(CACHE_KEY)
    if cached:
        return cached

    async with async_session() as session:
        result = await session.execute(
            select(Skill).order_by(Skill.category, Skill.level.desc())
        )
        skills = result.scalars().all()

        grouped = []
        for category, items in groupby(skills, key=attrgetter("category")):
            grouped.append({
                "category": category,
                "items": [
                    {"id": str(s.id), "name": s.name, "category": s.category, "level": s.level}
                    for s in items
                ],
            })

        await cache_set(CACHE_KEY, grouped, CACHE_TTL)
        return grouped


register_query_handler(GetSkillsQuery, handle_get_skills)
