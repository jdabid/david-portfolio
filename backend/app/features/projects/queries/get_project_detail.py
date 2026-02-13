"""
GetProjectDetail query — fetch a single project by slug.
"""

from dataclasses import dataclass

from sqlalchemy import select

from app.infrastructure.cache import cache_get, cache_set
from app.infrastructure.database import async_session
from app.features.projects.models import Project
from app.shared.mediator import Query, register_query_handler

CACHE_TTL = 300


@dataclass(frozen=True)
class GetProjectDetailQuery(Query):
    slug: str


async def handle_get_project_detail(query: GetProjectDetailQuery) -> dict | None:
    cache_key = f"projects:detail:{query.slug}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    async with async_session() as session:
        result = await session.execute(
            select(Project).where(Project.slug == query.slug)
        )
        project = result.scalar_one_or_none()
        if not project:
            return None

        data = {
            "id": str(project.id),
            "title": project.title,
            "slug": project.slug,
            "description": project.description,
            "long_description": project.long_description,
            "tags": project.tags,
            "image_url": project.image_url,
            "github_url": project.github_url,
            "live_url": project.live_url,
            "featured": project.featured,
        }

        await cache_set(cache_key, data, CACHE_TTL)
        return data


register_query_handler(GetProjectDetailQuery, handle_get_project_detail)
