"""
CreateProject command — CQRS write side.
Persists new project and invalidates projects cache.
"""

from dataclasses import dataclass

from app.infrastructure.cache import cache_delete
from app.infrastructure.database import async_session
from app.features.projects.models import Project
from app.shared.mediator import Command, register_command_handler


@dataclass(frozen=True)
class CreateProjectCommand(Command):
    data: dict


async def handle_create_project(command: CreateProjectCommand) -> dict:
    async with async_session() as session:
        project = Project(**command.data)
        session.add(project)
        await session.commit()
        await session.refresh(project)

        await cache_delete("projects:*")

        return {"id": str(project.id), "slug": project.slug}


register_command_handler(CreateProjectCommand, handle_create_project)
