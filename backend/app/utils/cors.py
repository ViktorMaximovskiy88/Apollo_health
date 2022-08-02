from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.settings import settings

origins = [
    "http://localhost:3000",
]


def cors(app):
    if settings.is_local:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
