from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.work_queue import WorkQueue


class Forward:
    @free_fall_migration(document_models=[WorkQueue])
    async def remove_unused_doc_name_index(self, session):
        # name_1 index is a non-text index for exact match (binary match),
        # but complex index of name locations.link_text is used for searching
        # and sorting doc name.
        await DocDocument.get_motor_collection().drop_index("name_1")


class Backward:
    ...
