from datetime import datetime, timezone
from logging import Logger as PyLogger
from typing import Any

from async_lru import alru_cache

from backend.app.utils.logger import Logger, create_and_log
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import (
    RetrievedDocument,
    RetrievedDocumentLocation,
    UpdateRetrievedDocument,
)
from backend.common.models.shared import DocDocumentLocation
from backend.common.models.site import FocusSectionConfig, Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User
from backend.common.services.document import create_doc_document_service
from backend.common.storage.text_handler import TextHandler
from backend.scrapeworker.common.models import DownloadContext
from backend.scrapeworker.common.utils import tokenize_string
from backend.scrapeworker.file_parsers import get_tags


class DocumentUpdater:
    def __init__(self, log: PyLogger, scrape_task: SiteScrapeTask, site: Site) -> None:
        self.log: PyLogger = log
        self.logger: Logger = Logger()
        self.text_handler: TextHandler = TextHandler()
        self.scrape_task: SiteScrapeTask = scrape_task
        self.site: Site = site

    @alru_cache
    async def get_user(self) -> User:
        user: User | None = await User.by_email("admin@mmitnetwork.com")
        if not user:
            raise Exception("No user found")
        return user

    def set_doc_name(self, parsed_content: dict, download: DownloadContext):
        self.log.debug(
            f"title='{parsed_content['title']}' link_text='{download.metadata.link_text}' file_name='{download.file_name}' request_url='{download.request.url}'"  # noqa
        )
        return (
            parsed_content["title"]
            or download.metadata.link_text
            or download.metadata.siblings_text
            or download.file_name
            or download.request.url
        )

    async def update_retrieved_document(
        self,
        document: RetrievedDocument,
        download: DownloadContext,
        parsed_content: dict,
        focus_configs: list[FocusSectionConfig] | None = None,
    ) -> UpdateRetrievedDocument:
        now: datetime = datetime.now(tz=timezone.utc)
        location = document.get_site_location(self.site.id)
        context_metadata = download.metadata.dict()
        new_location = None

        if location:
            location.link_text = download.metadata.link_text
            location.siblings_text = download.metadata.siblings_text
            location.context_metadata = context_metadata
            location.last_collected_date = now
        else:
            await get_tags(parsed_content, focus_configs=focus_configs)
            new_location = RetrievedDocumentLocation(
                base_url=download.metadata.base_url,
                first_collected_date=now,
                last_collected_date=now,
                site_id=self.site.id,
                url=download.request.url,
                context_metadata=context_metadata,
                link_text=download.metadata.link_text,
                siblings_text=download.metadata.siblings_text,
                url_therapy_tags=parsed_content["url_therapy_tags"],
                url_indication_tags=parsed_content["url_indication_tags"],
                link_therapy_tags=parsed_content["link_therapy_tags"],
                link_indication_tags=parsed_content["link_indication_tags"],
            )

        # Must handle locations separately to avoid overwriting concurrent updates
        if new_location:
            await RetrievedDocument.find({"_id": document.id}).update(
                {"$push": {"locations": new_location}}
            )
        elif location:
            await RetrievedDocument.find(
                {"_id": document.id, "locations.site_id": self.site.id}
            ).update({"$set": {"locations.$": location}})

        await document.update({"$set": {"last_collected_date": now}})

        return bool(new_location)

    async def update_doc_document(
        self,
        retrieved_document: RetrievedDocument,
    ):
        doc_document: DocDocument | None = await DocDocument.find_one(
            DocDocument.retrieved_document_id == retrieved_document.id
        )

        if not doc_document:
            raise Exception(f"DocDocument retrieved_document_id={retrieved_document.id} not found")

        self.log.debug(f"doc doc update -> {doc_document.id}")
        rt_doc_location = retrieved_document.get_site_location(self.site.id)
        location = doc_document.get_site_location(self.site.id)
        new_location = False

        if location and rt_doc_location:
            self.log.debug(f"doc doc update location -> site_id={self.site.id}")
            await DocDocument.find(
                {"_id": doc_document.id, "locations.site_id": self.site.id}
            ).update(
                {
                    "$set": {
                        "locations.$.link_text": rt_doc_location.link_text,
                        "locations.$.siblings_text": rt_doc_location.siblings_text,
                        "locations.$.last_collected_date": rt_doc_location.last_collected_date,
                    }
                }
            )
        elif rt_doc_location:
            new_location = True
            self.log.debug(f"doc doc new location -> site_id={self.site.id}")
            await DocDocument.find({"_id": doc_document.id}).update(
                {"$push": {"locations": DocDocumentLocation(**rt_doc_location.dict())}}
            )

        await doc_document.update(
            {"$set": {"last_collected_date": retrieved_document.last_collected_date}}
        )

        return new_location

    async def create_retrieved_document(
        self, parsed_content: dict[str, Any], download: DownloadContext, checksum: str, url: str
    ):
        self.log.debug("creating doc")
        now: datetime = datetime.now(tz=timezone.utc)
        name = self.set_doc_name(parsed_content, download)
        tokens = tokenize_string(parsed_content["text"])
        text_checksum: str = await self.text_handler.save_text(parsed_content["text"])
        context_metadata = download.metadata.dict()

        document = RetrievedDocument(
            file_size=download.file_size,
            checksum=checksum,
            text_checksum=text_checksum,
            content_checksum=parsed_content["content_checksum"],
            doc_type_confidence=parsed_content["confidence"],
            document_type=parsed_content["document_type"],
            doc_vectors=parsed_content["doc_vectors"],
            effective_date=parsed_content["effective_date"],
            end_date=parsed_content["end_date"],
            last_updated_date=parsed_content["last_updated_date"],
            last_reviewed_date=parsed_content["last_reviewed_date"],
            next_review_date=parsed_content["next_review_date"],
            next_update_date=parsed_content["next_update_date"],
            published_date=parsed_content["published_date"],
            file_extension=download.file_extension,
            content_type=download.content_type,
            identified_dates=parsed_content["identified_dates"],
            lang_code=parsed_content["lang_code"],
            metadata=parsed_content["metadata"],
            name=name,
            therapy_tags=parsed_content["therapy_tags"],
            indication_tags=parsed_content["indication_tags"],
            priority=parsed_content["priority"],
            first_collected_date=now,
            last_collected_date=now,
            token_count=len(tokens),
            doc_type_match=parsed_content["doc_type_match"],
            is_searchable=download.is_searchable,
            locations=[
                RetrievedDocumentLocation(
                    base_url=download.metadata.base_url,
                    first_collected_date=now,
                    last_collected_date=now,
                    site_id=self.site.id,
                    url=url,
                    context_metadata=context_metadata,
                    link_text=download.metadata.link_text,
                    siblings_text=download.metadata.siblings_text,
                    url_therapy_tags=parsed_content["url_therapy_tags"],
                    url_indication_tags=parsed_content["url_indication_tags"],
                    link_therapy_tags=parsed_content["link_therapy_tags"],
                    link_indication_tags=parsed_content["link_indication_tags"],
                )
            ],
        )

        await create_and_log(self.logger, await self.get_user(), document)
        return document

    async def create_doc_document(self, retrieved_document: RetrievedDocument) -> DocDocument:
        return await create_doc_document_service(retrieved_document, await self.get_user())
