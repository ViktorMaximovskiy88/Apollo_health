from beanie import PydanticObjectId

from backend.common.models.doc_document import DocDocument
from backend.common.services.lineage.insert_into_lineage import (
    insert_into_lineage_include_later_documents,
    insert_into_lineage_not_include_later_documents,
)


async def update_lineage(
    updating_doc_doc: DocDocument,
    old_prev_doc_doc_id: PydanticObjectId | None,
    new_prev_doc_doc_id: PydanticObjectId | None,
    include_later_documents: bool = False,
):
    if old_prev_doc_doc_id == new_prev_doc_doc_id:
        raise Exception(
            f"old_prev_doc_doc_id == new_prev_doc_doc_id: (old_prev_doc_doc_id: {old_prev_doc_doc_id}). \
                This should not be possible. There is a code error."
        )

    if include_later_documents:
        return await insert_into_lineage_include_later_documents(
            updating_doc_doc, new_prev_doc_doc_id, old_prev_doc_doc_id
        )
    else:
        return await insert_into_lineage_not_include_later_documents(
            updating_doc_doc, new_prev_doc_doc_id, old_prev_doc_doc_id
        )
