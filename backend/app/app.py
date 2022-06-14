from pathlib import Path
from typing import Any
from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.app.scripts.add_user import create_admin_user
from backend.common.db.init import init_db
from backend.common.db.migrations import run_migrations
from backend.common.core.config import is_local
from backend.app.routes import sites
from backend.app.utils.user import get_current_user, get_token_from_request
from backend.common.models.user import User
from routes import (
    auth,
    users,
    documents,
    change_log,
    site_scrape_tasks,
    content_extraction_tasks,
)

app = FastAPI()


@app.on_event("startup")
async def app_init():
    await init_db()
    if is_local:
        await run_migrations()
    if await User.count() == 0:
        user, plain_pass = await create_admin_user()
        print(f"Created admin user with email: {user}, password: {plain_pass}")


template_dir = Path(__file__).parent.joinpath("templates")
templates = Jinja2Templates(directory=template_dir)
frontend_build_dir = Path(__file__).parent.joinpath("../../frontend/build").resolve()

app.add_middleware(GZipMiddleware)

prefix = "/api/v1"
app.include_router(auth.router, prefix=prefix)
app.include_router(users.router, prefix=prefix)
app.include_router(change_log.router, prefix=prefix)
app.include_router(sites.router, prefix=prefix)
app.include_router(site_scrape_tasks.router, prefix=prefix)
app.include_router(documents.router, prefix=prefix)
app.include_router(content_extraction_tasks.router, prefix=prefix)
app.mount("/", StaticFiles(directory=frontend_build_dir, html=True), name="static")
