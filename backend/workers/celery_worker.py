"""
Celery worker entrypoint.
Run with: celery -A workers.celery_worker.app worker --loglevel=info
"""

from app.infrastructure.celery_app import celery_app as app  # noqa: F401
