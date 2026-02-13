"""
ListProjects query — CQRS read side.
Supports filtering by tag and featured flag. Uses Redis cache.
"""

from dataclasses import dataclass

from sqlalchemy import select

from app.infrastructure.cache import cache_get, cache_set
from app.infrastructure.database import async_session
from app.features.projects.models import Project
from app.shared.mediator import Query, register_query_handler

CACHE_TTL = 300


@dataclass(frozen=True)
class ListProjectsQuery(Query):
    tag: str | None = None
    featured: bool | None = None


async def handle_list_projects(query: ListProjectsQuery) -> list[dict]:
    cache_key = f"projects:list:tag={query.tag}:featured={query.featured}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    async with async_session() as session:
        stmt = select(Project).order_by(Project.sort_order, Project.created_at.desc())

        if query.tag:
            stmt = stmt.where(Project.tags.any(query.tag))
        if query.featured is not None:
            stmt = stmt.where(Project.featured == query.featured)

        result = await session.execute(stmt)
        projects = result.scalars().all()

        data = [
            {
                "id": str(p.id),
                "title": p.title,
                "slug": p.slug,
                "description": p.description,
                "tags": p.tags,
                "image_url": p.image_url,
                "featured": p.featured,
            }
            for p in projects
        ]

        await cache_set(cache_key, data, CACHE_TTL)
        return data


register_query_handler(ListProjectsQuery, handle_list_projects)
