from logging import Logger as PyLogger
from urllib.parse import urlparse

from beanie import PydanticObjectId

from backend.common.models.document import RetrievedDocument
from backend.scrapeworker.common.state_parser import guess_state_abbr


def tokenize_url(url: str):
    parsed = urlparse(url)
    return parsed.path.split("/")


def tokenize_path_part(part: str):
    match = guess_state_abbr(part)
    return match.group("state_abbr") if match else None


class LineageService:
    def __init__(self, log: PyLogger) -> None:
        self.log = log

    async def process_lineage_for_site(self, site_id: PydanticObjectId):
        docs = await RetrievedDocument.find({"locations.site_id": site_id}).to_list()
        print(len(docs))
        return docs

    async def process_lineage_for_doc_ids(self, doc_ids: list[PydanticObjectId]):
        docs = await RetrievedDocument.find({"_id": {"$in": doc_ids}}).to_list()
        print(len(docs))
        return docs

    def process_lineage_for_docs(self, docs: list[RetrievedDocument]):
        pass

    def determine_lineage(self, site_id: PydanticObjectId, doc: RetrievedDocument):
        print(site_id, doc)
        location = doc.get_site_location(site_id)
        print(location)
