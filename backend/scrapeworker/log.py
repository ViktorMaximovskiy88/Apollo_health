import traceback
import typer
from datetime import datetime
from backend.common.core.enums import SiteStatus
from backend.common.core.enums import TaskStatus
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from beanie.odm.operators.update.general import Set


async def log_error_status(scrape_task, site, message, task_status):
    now = datetime.now()
    site_status = (
        SiteStatus.QUALITY_HOLD if task_status == TaskStatus.FAILED else site.status
    )
    await site.update(
        Set(
            {
                Site.last_run_status: task_status,
                Site.last_run_time: now,
                Site.status: site_status,
            }
        )
    )
    await scrape_task.update(
        Set(
            {
                SiteScrapeTask.status: task_status,
                SiteScrapeTask.error_message: message,
                SiteScrapeTask.end_time: now,
            }
        )
    )


async def log_success(scrape_task: SiteScrapeTask, site: Site):
    typer.secho(f"Finished Task {scrape_task.id}", fg=typer.colors.BLUE)
    now = datetime.now()
    await site.update(
        Set({Site.last_run_status: TaskStatus.FINISHED, Site.last_run_time: now})
    )
    await scrape_task.update(
        Set(
            {
                SiteScrapeTask.status: TaskStatus.FINISHED,
                SiteScrapeTask.end_time: now,
            }
        )
    )


async def log_failure(scrape_task, site, ex):
    message = traceback.format_exc()
    traceback.print_exc()
    typer.secho(f"Task Failed {scrape_task.id}", fg=typer.colors.RED)
    await log_error_status(
        scrape_task=scrape_task,
        site=site,
        message=message,
        task_status=TaskStatus.FAILED,
    )


async def log_cancellation(scrape_task, site, ex):
    typer.secho(f"Task Canceled {scrape_task.id}", fg=typer.colors.RED)
    message = str(ex)
    await log_error_status(
        scrape_task=scrape_task,
        site=site,
        message=message,
        task_status=TaskStatus.CANCELED,
    )


async def log_not_found(scrape_task, site, ex):
    message = str(ex)
    typer.secho(f"Task Failed {scrape_task.id}", fg=typer.colors.RED)
    await log_error_status(
        scrape_task=scrape_task,
        site=site,
        message=message,
        task_status=TaskStatus.FAILED,
    )
