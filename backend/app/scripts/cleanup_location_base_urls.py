import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))
from backend.common.db.init import init_db
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.site import Site


async def cleanup_location_base_urls():
    site_to_url = {}
    async for site in Site.get_motor_collection().find({}):
        site_to_url[site["_id"]] = site["base_urls"][0]["url"]

    for Collection in [DocDocument, RetrievedDocument]:
        updates = []
        async for doc in Collection.get_motor_collection().find(
            {"locations.base_url": None}, {"locations": 1}
        ):
            base_url = site_to_url[doc["locations"][0]["site_id"]]
            print(base_url)
            updates.append(
                Collection.get_motor_collection().update_one(
                    {"_id": doc["_id"]}, {"$set": {"locations.0.base_url": base_url}}
                )
            )
        await asyncio.gather(*updates)


async def execute():
    await init_db()
    await cleanup_location_base_urls()


if __name__ == "__main__":
    asyncio.run(execute())
