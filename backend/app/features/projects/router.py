"""
Projects API endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.features.projects.schemas import CreateProjectRequest, ProjectListItem, ProjectResponse
from app.features.projects.commands.create_project import CreateProjectCommand
from app.features.projects.queries.list_projects import ListProjectsQuery
from app.features.projects.queries.get_project_detail import GetProjectDetailQuery
from app.shared.mediator import send_command, send_query

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectListItem])
async def list_projects(tag: str | None = None, featured: bool | None = None):
    """List all projects with optional tag and featured filters."""
    return await send_query(ListProjectsQuery(tag=tag, featured=featured))


@router.get("/{slug}", response_model=ProjectResponse)
async def get_project(slug: str):
    """Get project detail by slug."""
    result = await send_query(GetProjectDetailQuery(slug=slug))
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.post("", status_code=201)
async def create_project(body: CreateProjectRequest):
    """Create a new project."""
    return await send_command(CreateProjectCommand(data=body.model_dump()))
