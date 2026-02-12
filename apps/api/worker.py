"""
Entrypoint for running the arq worker process.

Usage:
    arq worker.WorkerSettings

This module re-exports WorkerSettings so arq can discover it.
"""

from app.workers import WorkerSettings  # noqa: F401
