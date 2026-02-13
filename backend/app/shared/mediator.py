"""
CQRS Mediator — dispatches Commands and Queries to their handlers.
Decouples the router layer from business logic.
"""

from dataclasses import dataclass
from typing import Any, Callable, TypeVar

T = TypeVar("T")

_command_handlers: dict[type, Callable] = {}
_query_handlers: dict[type, Callable] = {}


@dataclass(frozen=True)
class Command:
    """Base class for write operations."""
    pass


@dataclass(frozen=True)
class Query:
    """Base class for read operations."""
    pass


def register_command_handler(command_type: type, handler: Callable) -> None:
    _command_handlers[command_type] = handler


def register_query_handler(query_type: type, handler: Callable) -> None:
    _query_handlers[query_type] = handler


async def send_command(command: Command) -> Any:
    """Dispatch a command to its registered handler."""
    handler = _command_handlers.get(type(command))
    if not handler:
        raise ValueError(f"No handler registered for command: {type(command).__name__}")
    return await handler(command)


async def send_query(query: Query) -> Any:
    """Dispatch a query to its registered handler."""
    handler = _query_handlers.get(type(query))
    if not handler:
        raise ValueError(f"No handler registered for query: {type(query).__name__}")
    return await handler(query)
