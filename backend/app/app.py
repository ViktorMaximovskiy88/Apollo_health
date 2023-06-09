from pathlib import Path
from time import time
from typing import Any

import aiofiles
import jwt
import newrelic.agent
from fastapi import FastAPI, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException

from backend.app.core.settings import settings
from backend.app.routes import (
    app_config,
    change_log,
    comments,
    content_extraction_tasks,
    devtools,
    doc_documents,
    document_family,
    documents,
    payer_backbone,
    payer_family,
    proxies,
    site_scrape_tasks,
    sites,
    stats,
    task,
    therapy_master,
    translations,
    users,
    work_queues,
)
from backend.app.scripts.add_user import create_system_users
from backend.app.scripts.create_pipeline_registry import create_pipeline_registry
from backend.app.scripts.create_proxy_records import create_proxies
from backend.app.scripts.create_work_queues import create_default_work_queues
from backend.app.scripts.payer_backbone.load_payer_backbone import load_payer_backbone
from backend.app.utils.cors import cors
from backend.app.utils.logging import Logger, get_app_logger
from backend.app.utils.user import get_provider_detail
from backend.common.db.init import init_db
from backend.common.db.migrations import confirm_migration_quality, run_migrations
from backend.common.models.proxy import Proxy

app = FastAPI()
cors(app)  # local only
logger: Logger = get_app_logger()

frontend_html = None
template_dir = Path(__file__).parent.joinpath("templates")
templates = Jinja2Templates(directory=template_dir)
frontend_build_dir = Path(__file__).parent.joinpath("../../frontend/build").resolve()


@app.on_event("startup")
async def app_init():
    await init_db()

    # poor mans caching, do it up front on startup
    global frontend_html
    async with aiofiles.open(frontend_build_dir.joinpath("index.html")) as file:
        frontend_html = await file.read()

    if settings.is_local:
        if await confirm_migration_quality():
            await run_migrations()
    await create_system_users()
    if not settings.disable_proxies and await Proxy.count() == 0:
        await create_proxies()
    await create_default_work_queues()
    await load_payer_backbone()
    await create_pipeline_registry()


# must be first, reverse order...
@app.exception_handler(Exception)
async def last_chance_exception_handle(request, exc):
    message = str(exc)
    status_code = 500

    logger.exception(message)
    newrelic.agent.notice_error()

    result = await http_exception_handler(
        request, HTTPException(detail=message, status_code=status_code)
    )
    return result


@app.middleware("http")
async def frontend_routing(request: Request, call_next: Any):
    response = await call_next(request)
    if response.status_code == status.HTTP_404_NOT_FOUND and not request.url.path.startswith(
        "/api"
    ):
        return HTMLResponse(frontend_html)
    return response


# liveness
@app.get("/ping", include_in_schema=False)
async def ping():
    return {"ok": True}


@app.get("/api/v1/settings", include_in_schema=False)
async def react_settings():
    return settings.frontend


@app.get("/request-access", response_class=HTMLResponse, include_in_schema=False)
async def request_access(request: Request):
    return templates.TemplateResponse("request-access.html", {"request": request})


prefix = "/api/v1"
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
app.include_router(devtools.router, prefix=prefix)
app.include_router(payer_family.router, prefix=prefix)
app.include_router(stats.router, prefix=prefix)
app.include_router(comments.router, prefix=prefix)
app.include_router(therapy_master.router, prefix=prefix)
app.include_router(task.router, prefix=prefix)

app.mount("/", StaticFiles(directory=frontend_build_dir, html=True), name="static")

app.add_middleware(GZipMiddleware)


# TODO when/if we auth on backend, we can make user a global dep and re-use...
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # TODO if this stays, lets move it...
    auth_header = request.headers.get("authorization", None)
    user = "anon"
    user_id = None
    if auth_header:
        [_, token] = auth_header.split(" ")
        [signing_key, algorithm] = get_provider_detail(token)
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[algorithm],
            audience=settings.auth0.audience,
        )
        user = payload.get("https://mmit.com/email")

    logger.info(f"request_start='{request.method}_{request.url.path}' user='{user}'")
    start_time = time()
    response = await call_next(request)
    process_time = (time() - start_time) * 1000
    format_time = "{0:.2f}".format(process_time)
    logger.info(
        f"request_stop='{request.method}_{request.url.path}' user='{user}' duration='{format_time}ms'"  # noqa
    )

    newrelic.agent.add_custom_attribute("user_id", user_id)
    newrelic.agent.add_custom_attribute("user", user)

    return response
