import logging

from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument


class Forward:
    @free_fall_migration(document_models=[DocDocument, RetrievedDocument])
    async def doc_doc_file_ext(self, session):

        # getting crafty, we know these are pdfs are the lions share
        # right now prod has 39 non pdfs, lets let it roll #yolo
        non_pdf_match_count = 0
        non_pdf_update_count = 0
        async for result in RetrievedDocument.find({"file_extension": {"$ne": "pdf"}}):
            non_pdf_match_count += 1
            doc_doc: DocDocument = DocDocument.find_one({"retrieved_document_id": result.id})
            if doc_doc:
                await doc_doc.update({"$set": {"file_extension": result.file_extension}})
                non_pdf_update_count += 1

        logging.info(
            f"updating non-pdfs -> matched_count={non_pdf_match_count} modified_count={non_pdf_update_count}"  # noqa
        )

        # now we can move fast with this guy; the rest are pdf
        result = await DocDocument.get_motor_collection().update_many(
            {"file_extension": {"$exists": False}},
            {"$set": {"file_extension": "pdf"}},
        )

        logging.info(
            f"updating pdfs -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )


class Backward:
    @free_fall_migration(document_models=[DocDocument])
    async def doc_doc_file_ext(self, session):
        logging.info("there is no undo here, again, again. rough life")
        pass
