from datetime import datetime, timezone
from typing import Any

from async_lru import alru_cache
from beanie.odm.operators.update.general import Set

from backend.app.utils.logger import Logger, create_and_log
from backend.common.models.doc_document import (
    DocDocument,
    IndicationTag,
    TherapyTag,
    calc_final_effective_date,
)
from backend.common.models.document import RetrievedDocument, UpdateRetrievedDocument
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User
from backend.common.storage.text_handler import TextHandler
from backend.scrapeworker.common.models import DownloadContext


class DocumentUpdater:
    def __init__(self, log: Logger, scrape_task: SiteScrapeTask, site: Site) -> None:
        self.log = log
        self.logger = Logger()
        self.text_handler = TextHandler()
        self.scrape_task = scrape_task
        self.site = site

    @alru_cache
    async def get_user(self) -> User:
        user = await User.by_email("admin@mmitnetwork.com")
        if not user:
            raise Exception("No user found")
        return user

    def set_doc_name(self, parsed_content: dict, download: DownloadContext):
        self.log.info(
            f"title='{parsed_content['title']}' link_text='{download.metadata.link_text}' file_name='{download.file_name}' request_url='{download.request.url}'"  # noqa
        )
        return (
            parsed_content["title"]
            or download.metadata.link_text
            or download.file_name
            or download.request.url
        )

    # TODO we temporarily update allthethings. as our code matures, this likely dies
    async def update_retrieved_document(
        self,
        document: RetrievedDocument,
        download: DownloadContext,
        parsed_content: dict,
    ) -> UpdateRetrievedDocument:
        now = datetime.now(tz=timezone.utc)
        name = self.set_doc_name(parsed_content, download)
        updated_doc = UpdateRetrievedDocument(
            context_metadata=download.metadata.dict(),
            doc_type_confidence=parsed_content["confidence"],
            document_type=parsed_content["document_type"],
            effective_date=parsed_content["effective_date"],
            end_date=parsed_content["end_date"],
            last_updated_date=parsed_content["last_updated_date"],
            last_reviewed_date=parsed_content["last_reviewed_date"],
            next_review_date=parsed_content["next_review_date"],
            next_update_date=parsed_content["next_update_date"],
            published_date=parsed_content["published_date"],
            identified_dates=parsed_content["identified_dates"],
            lang_code=parsed_content["lang_code"],
            last_collected_date=now,
            therapy_tags=parsed_content["therapy_tags"],
            indication_tags=parsed_content["indication_tags"],
            metadata=parsed_content["metadata"],
            name=name,
            scrape_task_id=self.scrape_task.id,
            text_checksum=document.text_checksum,
        )
        await document.update(Set(updated_doc.dict(exclude_unset=True)))
        return updated_doc

    async def update_doc_document(
        self,
        retrieved_document: RetrievedDocument,
        new_therapy_tags: list[TherapyTag],
        new_indicate_tags: list[IndicationTag],
    ):
        doc_document = await DocDocument.find_one(
            DocDocument.retrieved_document_id == retrieved_document.id
        )
        if doc_document:
            if self.site.scrape_method_configuration.allow_docdoc_updates is True:
                doc_document.therapy_tags = retrieved_document.therapy_tags
                doc_document.indication_tags = retrieved_document.indication_tags
            else:
                doc_document.therapy_tags = doc_document.therapy_tags + new_therapy_tags
                doc_document.indication_tags = doc_document.indication_tags + new_indicate_tags

            doc_document.text_checksum = (
                retrieved_document.text_checksum
            )  # Can be removed after text added to older docs
            doc_document.last_collected_date = retrieved_document.last_collected_date
            await doc_document.save()
        else:
            await self.create_doc_document(retrieved_document)

    async def create_retrieved_document(
        self, parsed_content: dict[str, Any], download: DownloadContext, checksum: str, url: str
    ):
        self.log.info("creating doc")
        now = datetime.now(tz=timezone.utc)
        name = self.set_doc_name(parsed_content, download)
        text_checksum = await self.text_handler.save_text(parsed_content["text"])
        document = RetrievedDocument(
            base_url=download.metadata.base_url,
            checksum=checksum,
            text_checksum=text_checksum,
            context_metadata=download.metadata.dict(),
            doc_type_confidence=parsed_content["confidence"],
            document_type=parsed_content["document_type"],
            effective_date=parsed_content["effective_date"],
            end_date=parsed_content["end_date"],
            last_updated_date=parsed_content["last_updated_date"],
            last_reviewed_date=parsed_content["last_reviewed_date"],
            next_review_date=parsed_content["next_review_date"],
            next_update_date=parsed_content["next_update_date"],
            published_date=parsed_content["published_date"],
            file_extension=download.file_extension,
            content_type=download.content_type,
            first_collected_date=now,
            identified_dates=parsed_content["identified_dates"],
            lang_code=parsed_content["lang_code"],
            last_collected_date=now,
            metadata=parsed_content["metadata"],
            name=name,
            scrape_task_id=self.scrape_task.id,
            site_id=self.site.id,
            url=url,
            therapy_tags=parsed_content["therapy_tags"],
            indication_tags=parsed_content["indication_tags"],
        )
        await create_and_log(self.logger, await self.get_user(), document)
        return document

    async def create_doc_document(self, retrieved_document: RetrievedDocument):
        doc_document = DocDocument(
            site_id=retrieved_document.site_id,
            retrieved_document_id=retrieved_document.id,  # type: ignore
            name=retrieved_document.name,
            checksum=retrieved_document.checksum,
            text_checksum=retrieved_document.text_checksum,
            document_type=retrieved_document.document_type,
            doc_type_confidence=retrieved_document.doc_type_confidence,
            end_date=retrieved_document.end_date,
            effective_date=retrieved_document.effective_date,
            last_updated_date=retrieved_document.last_updated_date,
            last_reviewed_date=retrieved_document.last_reviewed_date,
            next_review_date=retrieved_document.next_review_date,
            next_update_date=retrieved_document.next_update_date,
            published_date=retrieved_document.published_date,
            lang_code=retrieved_document.lang_code,
            first_collected_date=retrieved_document.first_collected_date,
            last_collected_date=retrieved_document.last_collected_date,
            link_text=retrieved_document.context_metadata["link_text"],
            url=retrieved_document.url,
            base_url=retrieved_document.base_url,
            therapy_tags=retrieved_document.therapy_tags,
            indication_tags=retrieved_document.indication_tags,
            file_extension=retrieved_document.file_extension,
            identified_dates=retrieved_document.identified_dates,
        )
        doc_document.final_effective_date = calc_final_effective_date(doc_document)
        await create_and_log(self.logger, await self.get_user(), doc_document)