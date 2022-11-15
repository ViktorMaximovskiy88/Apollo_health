from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.app.core.settings import settings
from backend.app.routes import (
    app_config,
    auth,
    change_log,
    comments,
    content_extraction_tasks,
    doc_documents,
    document_family,
    documents,
    lineage,
    payer_backbone,
    payer_family,
    proxies,
    site_scrape_tasks,
    sites,
    stats,
    therapy_master,
    translations,
    users,
    work_queues,
)
from backend.app.scripts.add_user import create_system_users
from backend.app.scripts.create_proxy_records import create_proxies
from backend.app.scripts.create_work_queues import create_default_work_queues
from backend.app.scripts.payer_backbone.load_payer_backbone import load_payer_backbone
from backend.app.utils.cors import cors
from backend.common.db.init import init_db
from backend.common.db.migrations import confirm_migration_quality, run_migrations
from backend.common.models.proxy import Proxy

app = FastAPI()
cors(app)  # local only


@app.on_event("startup")
async def app_init():
    await init_db()
    if settings.is_local:
        if await confirm_migration_quality():
            await run_migrations()
    await create_system_users()
    if not settings.disable_proxies and await Proxy.count() == 0:
        await create_proxies()
    await create_default_work_queues()
    await load_payer_backbone()


template_dir = Path(__file__).parent.joinpath("templates")
templates = Jinja2Templates(directory=template_dir)
frontend_build_dir = Path(__file__).parent.joinpath("../../frontend/build").resolve()


# liveness
@app.get("/ping", include_in_schema=False)
async def ping():
    return {"ok": True}


@app.get("/api/v1/settings", include_in_schema=False)
async def react_settings():
    return settings.frontend


@app.get("/api/v1/auth/authorize", response_class=HTMLResponse, tags=["Auth"])
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


app.add_middleware(GZipMiddleware)

prefix = "/api/v1"
app.include_router(auth.router, prefix=prefix)
app.include_router(users.router, prefix=prefix)
app.include_router(change_log.router, prefix=prefix)
app.include_router(sites.router, prefix=prefix)
app.include_router(site_scrape_tasks.router, prefix=prefix)
app.include_router(documents.router, prefix=prefix)
app.include_router(content_extraction_tasks.router, prefix=prefix)
app.include_router(proxies.router, prefix=prefix)
app.include_router(doc_documents.router, prefix=prefix)
app.include_router(work_queues.router, prefix=prefix)
app.include_router(translations.router, prefix=prefix)
app.include_router(document_family.router, prefix=prefix)
app.include_router(payer_backbone.router, prefix=prefix)
app.include_router(app_config.router, prefix=prefix)
app.include_router(lineage.router, prefix=prefix)
app.include_router(payer_family.router, prefix=prefix)
app.include_router(stats.router, prefix=prefix)
app.include_router(comments.router, prefix=prefix)
app.include_router(therapy_master.router, prefix=prefix)


@app.middleware("http")
async def frontend_routing(request: Request, call_next: Any):
    response = await call_next(request)

    if response.status_code == status.HTTP_404_NOT_FOUND and not request.url.path.startswith(
        "/api"
    ):
        with open(frontend_build_dir.joinpath("index.html")) as file:
            return HTMLResponse(file.read())

    return response


app.mount("/", StaticFiles(directory=frontend_build_dir, html=True), name="static")
