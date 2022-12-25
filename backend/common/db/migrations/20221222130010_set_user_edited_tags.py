from pprint import pprint

from beanie import free_fall_migration

from backend.common.models.change_log import ChangeLog
from backend.common.models.doc_document import DocDocument


async def find_changes(tag_type: str):
    match = {
        "collection": "DocDocument",
        "delta.path": {"$regex": rf"/{tag_type}/\d/focus", "$options": "i"},
        "action": "UPDATE",
    }
    changed_docs = await ChangeLog.aggregate(
        aggregation_pipeline=[
            {"$match": match},
            {"$unwind": {"path": "$delta"}},
            {"$match": match},
            {
                "$group": {
                    "_id": "$target_id",
                    "log_ids": {"$addToSet": "$_id"},
                    "count": {"$count": {}},
                }
            },
        ]
    ).to_list()

    # kinda brutal...
    # looking for shortcut hueristic...
    pprint(changed_docs)


class Forward:
    @free_fall_migration(document_models=[ChangeLog, DocDocument])
    async def set_user_edited_fields(self, session):

        # first get code for changed tags by doc with log entries
        await find_changes("therapy_tags")
        await find_changes("indication_tags")


class Backward:
    ...
