import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))
from datetime import datetime, timezone

from backend.common.db.init import init_db
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask


async def run():
    sep27_noon = datetime(2022, 9, 27, 16, tzinfo=timezone.utc)
    sep28_noon = datetime(2022, 9, 28, 16, tzinfo=timezone.utc)
    sep27_1pm = datetime(2022, 9, 27, 18, tzinfo=timezone.utc)
    sep28_1pm = datetime(2022, 9, 28, 18, tzinfo=timezone.utc)
    sep29_noon = datetime(2022, 9, 29, 16, tzinfo=timezone.utc)
    sep29_1pm = datetime(2022, 9, 29, 18, tzinfo=timezone.utc)
    i = 0
    async for site in Site.find(
        {"last_run_time": {"$gt": datetime(2022, 9, 27, tzinfo=timezone.utc)}}
    ):
        next_q = SiteScrapeTask.find_one(
            {"site_id": site.id, "queued_time": {"$gte": sep29_noon, "$lte": sep29_1pm}}
        )
        bad_q = SiteScrapeTask.find_one(
            {"site_id": site.id, "queued_time": {"$gte": sep28_noon, "$lte": sep28_1pm}}
        )
        prev_q = SiteScrapeTask.find_one(
            {"site_id": site.id, "queued_time": {"$gte": sep27_noon, "$lte": sep27_1pm}}
        )
        bad, prev, next = await asyncio.gather(bad_q, prev_q, next_q)
        if bad and prev and next:
            n_bad = len(bad.retrieved_document_ids)
            n_prev = len(prev.retrieved_document_ids)
            n_next = len(next.retrieved_document_ids)

            diff_count_bad_prev = n_bad - n_prev
            diff_count_next_bad = n_next - n_bad
            diff_count_next_prev = n_next - n_prev
            discrep_bad_prev = prev.retrieved_document_ids and diff_count_bad_prev > 50
            discrep_next_bad = bad.retrieved_document_ids and diff_count_next_bad > 50
            discrep_next_prev = prev.retrieved_document_ids and diff_count_next_prev > 50

            if discrep_bad_prev or discrep_next_bad or discrep_next_prev:
                i += 1
                print(i, site.name, discrep_bad_prev, discrep_next_bad, discrep_next_prev)
            elif n_bad and n_prev:
                # print(i, site.name, site.scrape_method_configuration.url_keywords)
                pass


async def execute():
    await init_db()
    await run()


if __name__ == "__main__":
    asyncio.run(execute())
