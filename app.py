"""Compatibility backend entry point for ShopPilot AI.

The browser client is implemented only in ``frontend/`` with React. This file
exposes the FastAPI application for tools that expect a root-level ``app.py``.
"""

from backend.app.main import app

__all__ = ["app"]
