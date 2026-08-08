from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.database.load_models  # noqa: F401

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware

OPENAPI_TAGS = [
    {"name": "health", "description": "Liveness"},
    {"name": "auth", "description": "Login, refresh, logout"},
    {"name": "products", "description": "Product CRUD"},
    {"name": "materials", "description": "Product materials"},
    {"name": "sustainability", "description": "Product sustainability"},
    {"name": "certifications", "description": "Product certifications"},
    {"name": "documents", "description": "Product documents"},
    {"name": "images", "description": "Product images"},
    {"name": "lookups", "description": "Cert types and authorities"},
    {"name": "publish", "description": "Publish product and download QR"},
    {"name": "passport", "description": "Public passport (no auth)"},
    {"name": "dashboard", "description": "Summary counts"},
    {"name": "analytics", "description": "QR scan analytics"},
]


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(debug=settings.debug)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=OPENAPI_TAGS,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # So the SPA can read QR filename ({public_uuid}.png) after download.
        expose_headers=["Content-Disposition"],
    )
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = create_app()
