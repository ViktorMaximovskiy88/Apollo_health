from logging import Logger as PyLogger
from urllib.parse import urlparse

from beanie import PydanticObjectId

from backend.common.models.document import RetrievedDocument
from backend.scrapeworker.common.state_parser import guess_state_abbr
from backend.scrapeworker.common.utils import date_rgxs, label_rgxs


def tokenize_url(url: str):
    parsed = urlparse(url)
    return parsed.path.split("/")


def jaccard(a: list, b: list):
    intersection = len(list(set(a).intersection(b)))
    union = (len(a) + len(b)) - intersection
    return float(intersection) / union


def unique_by_attr(items: list[any], attr: str) -> list:
    return list(set([getattr(item, attr) for item in items]))


class LineageService:
    def __init__(self, log: PyLogger) -> None:
        self.log = log

    async def process_lineage_for_site(self, site_id: PydanticObjectId):
        docs = await RetrievedDocument.find({"locations.site_id": site_id}).to_list()
        return docs

    async def process_lineage_for_site_url(self, site_id: PydanticObjectId, url: str):
        docs = await RetrievedDocument.find(
            {"locations.site_id": site_id, "locations.url": url}
        ).to_list()
        return docs

    async def process_lineage_for_site_doc_type(
        self, site_id: PydanticObjectId, document_type: str
    ):
        docs = await RetrievedDocument.find(
            {"locations.site_id": site_id, "document_type": document_type}
        ).to_list()
        return docs

    def determine_lineage(self, site_id: PydanticObjectId, doc: RetrievedDocument):
        print(site_id, doc)
        location = doc.get_site_location(site_id)
        print(location)
