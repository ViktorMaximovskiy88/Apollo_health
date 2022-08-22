from beanie import iterative_migration

# from backend.common.models.document import RetrievedDocument
from backend.common.models.site_scrape_task import NoDocIdScrapeTask, SiteScrapeTask


class Forward:
    @iterative_migration()
    async def add_doc_ids(self, input_document: NoDocIdScrapeTask, output_document: SiteScrapeTask):
        # TODO is there a better way to unhave this?
        pass
        # ret_docs = await RetrievedDocument
        #       .find(RetrievedDocument.scrape_task_id == input_document.id).to_list()
        # ret_doc_ids = list(ret_doc.id for ret_doc in ret_docs)
        # output_document.retrieved_document_ids = ret_doc_ids


class Backward:
    @iterative_migration()
    async def remove_doc_ids(
        self, input_document: SiteScrapeTask, output_document: NoDocIdScrapeTask
    ):
        output_document.retrieved_document_ids = None
