from datetime import datetime
from random import random
from unittest.mock import Mock

import pytest
import pytest_asyncio

from backend.common.core.enums import TagUpdateStatus
from backend.common.db.init import init_db
from backend.common.models.doc_document import DocDocument, DocDocumentLocation
from backend.common.models.document import RetrievedDocument, RetrievedDocumentLocation
from backend.common.models.shared import IndicationTag, TherapyTag
from backend.common.models.site import ScrapeMethodConfiguration, Site
from backend.common.services.tag_compare import DocumentSection, SectionLineage, TagCompare
from backend.common.storage.client import BaseS3Client
from backend.common.test.test_utils import mock_s3_client  # noqa


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)


@pytest_asyncio.fixture()
def tag_compare():
    return TagCompare()


@pytest_asyncio.fixture(autouse=True)
async def site():
    site = await Site(
        name="Test",
        scrape_method="",
        scrape_method_configuration=ScrapeMethodConfiguration(
            document_extensions=[],
            url_keywords=[],
            proxy_exclusions=[],
            follow_links=False,
            follow_link_keywords=[],
            follow_link_url_keywords=[],
        ),
        disabled=False,
        cron="0 * * * *",
    ).save()
    return site


def simple_ret_doc(
    site: Site, therapy_tags: list[TherapyTag] = [], indication_tags: list[IndicationTag] = []
) -> RetrievedDocument:
    return RetrievedDocument(
        name="test",
        checksum="test",
        text_checksum="test",
        first_collected_date=datetime.now(),
        last_collected_date=datetime.now(),
        therapy_tags=therapy_tags,
        indication_tags=indication_tags,
        locations=[
            RetrievedDocumentLocation(
                site_id=site.id,
                first_collected_date=datetime.now(),
                last_collected_date=datetime.now(),
                url="https://www.example.com/doc",
                base_url="https://www.example.com/",
                link_text="",
                closest_heading="",
                siblings_text=None,
            )
        ],
    )


def simple_doc_doc(
    site: Site,
    retrieved_doc: RetrievedDocument,
    therapy_tags: list[TherapyTag] = [],
    indication_tags: list[IndicationTag] = [],
):
    return DocDocument(
        name="test",
        retrieved_document_id=retrieved_doc.id,
        checksum="test",
        text_checksum="test",
        first_collected_date=datetime.now(),
        last_collected_date=datetime.now(),
        therapy_tags=therapy_tags,
        indication_tags=indication_tags,
        locations=[
            DocDocumentLocation(
                site_id=site.id,
                first_collected_date=datetime.now(),
                last_collected_date=datetime.now(),
                url="https://www.example.com/doc",
                base_url="https://www.example.com/",
                link_text="",
                closest_heading="",
                siblings_text=None,
            )
        ],
    )


def simple_therapy_tag(
    focus: bool = False, text_area: tuple[int, int] | None = (0, 100), page: int = 0, key=False
):
    return TherapyTag(
        text="text_test",
        page=page,
        code=str(random()),
        name="name_test",
        key=key,
        focus=focus,
        text_area=text_area,
    )


def simple_indication_tag(
    focus: bool = False, text_area: tuple[int, int] | None = (0, 100), page: int = 0, key=False
):
    return IndicationTag(
        text="text_test",
        page=page,
        code=round(random() * 1000),
        key=key,
        focus=focus,
        text_area=text_area,
    )


def group_by_status(tags: list[TherapyTag] | list[IndicationTag]):
    added = [tag for tag in tags if tag.update_status == TagUpdateStatus.ADDED]
    removed = [tag for tag in tags if tag.update_status == TagUpdateStatus.REMOVED]
    changed = [tag for tag in tags if tag.update_status == TagUpdateStatus.CHANGED]
    no_status = [tag for tag in tags if tag.update_status is None]
    assert len(added) + len(removed) + len(changed) + len(no_status) == len(tags)
    return {
        TagUpdateStatus.ADDED: added,
        TagUpdateStatus.REMOVED: removed,
        TagUpdateStatus.CHANGED: changed,
        "None": no_status,
    }


class TestTagChange:
    @pytest.mark.asyncio
    async def test_tag_diffs(
        self,
        mock_s3_client,  # noqa
        monkeypatch: pytest.MonkeyPatch,
        tag_compare: TagCompare,
        site: Site,
    ):
        doc_text = [
            bytes(
                "string one\nstring two",
                "utf-8",
            ),
            bytes(
                "string one\nstring three",
                "utf-8",
            ),
        ]
        mock = Mock(side_effect=doc_text)
        monkeypatch.setattr(BaseS3Client, "read_object", mock)

        ther_tags = [
            simple_therapy_tag(focus=True, text_area=(0, 100)),
            simple_therapy_tag(focus=False, text_area=(0, 100)),
        ]
        indi_tags = [
            simple_indication_tag(focus=True, text_area=(0, 100)),
            simple_indication_tag(focus=False, text_area=(0, 100)),
        ]
        ret_doc = await simple_ret_doc(
            site=site, therapy_tags=ther_tags, indication_tags=indi_tags
        ).save()
        doc_doc = await simple_doc_doc(
            site=site, retrieved_doc=ret_doc, therapy_tags=ther_tags, indication_tags=indi_tags
        ).save()

        final_ther, final_indi = await tag_compare.execute(ret_doc, doc_doc)
        assert len(final_ther) == 2
        assert len(final_indi) == 2
        changed_ther = group_by_status(final_ther)[TagUpdateStatus.CHANGED]
        assert len(changed_ther) == 2
        changed_indi = group_by_status(final_indi)[TagUpdateStatus.CHANGED]
        assert len(changed_indi) == 2

    @pytest.mark.asyncio
    async def test_ignore_dates(
        self,
        mock_s3_client,  # noqa
        monkeypatch: pytest.MonkeyPatch,
        tag_compare: TagCompare,
        site: Site,
    ):
        doc_text = [bytes("date 12/25/21 test", "utf-8"), bytes("date 12/25/20 test", "utf-8")]
        mock = Mock(side_effect=doc_text)
        monkeypatch.setattr(BaseS3Client, "read_object", mock)

        ther_tags = [
            simple_therapy_tag(focus=True, text_area=(0, 100)),
        ]
        indi_tags = [
            simple_indication_tag(focus=True, text_area=(0, 100)),
        ]
        ret_doc = await simple_ret_doc(
            site=site, therapy_tags=ther_tags, indication_tags=indi_tags
        ).save()
        doc_doc = await simple_doc_doc(
            site=site, retrieved_doc=ret_doc, therapy_tags=ther_tags, indication_tags=indi_tags
        ).save()

        final_ther, final_indi = await tag_compare.execute(ret_doc, doc_doc)
        assert len(final_ther) == 1
        assert len(final_indi) == 1
        ther_no_change = group_by_status(final_ther)["None"]
        assert len(ther_no_change) == 1
        assert ther_no_change[0].code == ther_tags[0].code
        indi_no_change = group_by_status(final_indi)["None"]
        assert len(indi_no_change) == 1
        assert indi_no_change[0].code == indi_tags[0].code

    @pytest.mark.asyncio
    async def test_ignore_pages(
        self,
        mock_s3_client,  # noqa
        monkeypatch: pytest.MonkeyPatch,
        tag_compare: TagCompare,
        site: Site,
    ):
        doc_text = [bytes("page number test 2", "utf-8"), bytes("page number test 1", "utf-8")]
        mock = Mock(side_effect=doc_text)
        monkeypatch.setattr(BaseS3Client, "read_object", mock)

        ther_tags = [
            simple_therapy_tag(focus=True, text_area=(0, 100)),
        ]
        indi_tags = [
            simple_indication_tag(focus=True, text_area=(0, 100)),
        ]
        ret_doc = await simple_ret_doc(
            site=site, therapy_tags=ther_tags, indication_tags=indi_tags
        ).save()
        doc_doc = await simple_doc_doc(
            site=site, retrieved_doc=ret_doc, therapy_tags=ther_tags, indication_tags=indi_tags
        ).save()

        final_ther, final_indi = await tag_compare.execute(ret_doc, doc_doc)
        assert len(final_ther) == 1
        assert len(final_indi) == 1
        ther_no_change = group_by_status(final_ther)["None"]
        assert len(ther_no_change) == 1
        assert ther_no_change[0].code == ther_tags[0].code
        indi_no_change = group_by_status(final_indi)["None"]
        assert len(indi_no_change) == 1
        assert indi_no_change[0].code == indi_tags[0].code

    @pytest.mark.asyncio
    async def test_handle_repeated_lines(
        self,
        mock_s3_client,  # noqa
        monkeypatch: pytest.MonkeyPatch,
        tag_compare: TagCompare,
        site: Site,
    ):
        doc_text = [
            bytes("string 1\nthis is a footer\nstring 2\nthis is a footer\n", "utf-8"),
            bytes("string 1\ndifferent footer here\nstring 2\ndifferent footer here\n", "utf-8"),
        ]
        mock = Mock(side_effect=doc_text)
        monkeypatch.setattr(BaseS3Client, "read_object", mock)

        ther_tags = [
            simple_therapy_tag(focus=True, text_area=(0, 100)),
        ]
        indi_tags = [
            simple_indication_tag(focus=True, text_area=(0, 100)),
        ]
        ret_doc = await simple_ret_doc(
            site=site, therapy_tags=ther_tags, indication_tags=indi_tags
        ).save()
        doc_doc = await simple_doc_doc(
            site=site, retrieved_doc=ret_doc, therapy_tags=ther_tags, indication_tags=indi_tags
        ).save()

        final_ther, final_indi = await tag_compare.execute(ret_doc, doc_doc)
        assert len(final_ther) == 1
        assert len(final_indi) == 1
        ther_no_change = group_by_status(final_ther)["None"]
        assert len(ther_no_change) == 1
        assert ther_no_change[0].code == ther_tags[0].code
        indi_no_change = group_by_status(final_indi)["None"]
        assert len(indi_no_change) == 1
        assert indi_no_change[0].code == indi_tags[0].code

    @pytest.mark.asyncio
    async def test_repeated_lines_different_tags(
        self,
        mock_s3_client,  # noqa
        monkeypatch: pytest.MonkeyPatch,
        tag_compare: TagCompare,
        site: Site,
    ):
        doc_text = [
            bytes("string 1\nthis is a footer\nstring 2\nthis is a footer\n", "utf-8"),
            bytes("string 1\ndifferent footer\nstring 2\ndifferent footer\n", "utf-8"),
        ]
        mock = Mock(side_effect=doc_text)
        monkeypatch.setattr(BaseS3Client, "read_object", mock)

        ther_tags = [
            simple_therapy_tag(focus=True, text_area=(0, 26)),
        ]
        indi_tags = [
            simple_indication_tag(focus=True, text_area=(26, 51)),
        ]
        ret_doc = await simple_ret_doc(
            site=site, therapy_tags=ther_tags, indication_tags=indi_tags
        ).save()
        doc_doc = await simple_doc_doc(
            site=site, retrieved_doc=ret_doc, therapy_tags=ther_tags, indication_tags=indi_tags
        ).save()

        final_ther, final_indi = await tag_compare.execute(ret_doc, doc_doc)
        assert len(final_ther) == 1
        assert len(final_indi) == 1
        ther_no_change = group_by_status(final_ther)["None"]
        assert len(ther_no_change) == 1
        assert ther_no_change[0].code == ther_tags[0].code
        indi_no_change = group_by_status(final_indi)["None"]
        assert len(indi_no_change) == 1
        assert indi_no_change[0].code == indi_tags[0].code

    @pytest.mark.asyncio
    async def test_tags_no_diff(
        self,
        mock_s3_client,  # noqa
        monkeypatch: pytest.MonkeyPatch,
        tag_compare: TagCompare,
        site: Site,
    ):
        doc_text = [bytes("string one", "utf-8"), bytes("string two", "utf-8")]
        mock = Mock(side_effect=doc_text)
        monkeypatch.setattr(BaseS3Client, "read_object", mock)

        ther_tags = [
            simple_therapy_tag(focus=True, text_area=(0, 4)),
            simple_therapy_tag(focus=False, text_area=(0, 4)),
        ]
        indi_tags = [
            simple_indication_tag(focus=True, text_area=(0, 4)),
            simple_indication_tag(focus=False, text_area=(0, 4)),
        ]
        ret_doc = await simple_ret_doc(
            site=site, therapy_tags=ther_tags, indication_tags=indi_tags
        ).save()
        doc_doc = await simple_doc_doc(
            site=site, retrieved_doc=ret_doc, therapy_tags=ther_tags, indication_tags=indi_tags
        ).save()

        final_ther, final_indi = await tag_compare.execute(ret_doc, doc_doc)
        assert len(final_ther) == 2
        assert len(final_indi) == 2
        for tag in final_ther:
            assert tag.update_status is None
        for tag in final_indi:
            assert tag.update_status is None


class TestTagAddRemove:
    @pytest.mark.asyncio
    async def test_added_tag(
        self,
        mock_s3_client,  # noqa
        monkeypatch: pytest.MonkeyPatch,
        tag_compare: TagCompare,
        site: Site,
    ):
        doc_text = [bytes("string two", "utf-8"), bytes("string two", "utf-8")]
        mock = Mock(side_effect=doc_text)
        monkeypatch.setattr(BaseS3Client, "read_object", mock)

        ther_tag_one = simple_therapy_tag(focus=True, text_area=(0, 20))
        ther_tag_two = simple_therapy_tag(focus=False, text_area=(0, 20))
        indi_tag_one = simple_indication_tag(focus=True, text_area=(0, 20))
        indi_tag_two = simple_indication_tag(focus=False, text_area=(0, 20))
        ret_doc = await simple_ret_doc(
            site=site,
            therapy_tags=[ther_tag_one, ther_tag_two],
            indication_tags=[indi_tag_one, indi_tag_two],
        ).save()
        doc_doc = await simple_doc_doc(
            site=site,
            retrieved_doc=ret_doc,
            therapy_tags=[ther_tag_one],
            indication_tags=[indi_tag_one],
        ).save()

        therapy_tags, indication_tags = await tag_compare.execute(ret_doc, doc_doc)
        assert len(therapy_tags) == 2
        assert len(indication_tags) == 2
        added_tags = group_by_status(therapy_tags)[TagUpdateStatus.ADDED]
        assert len(added_tags) == 1
        assert added_tags[0].code == ther_tag_two.code
        added_tags = group_by_status(indication_tags)[TagUpdateStatus.ADDED]
        assert len(added_tags) == 1
        assert added_tags[0].code == indi_tag_two.code

    @pytest.mark.asyncio
    async def test_non_focus_tags(
        self,
        mock_s3_client,  # noqa
        monkeypatch: pytest.MonkeyPatch,
        tag_compare: TagCompare,
        site: Site,
    ):
        doc_text = [bytes("string one", "utf-8"), bytes("string two", "utf-8")]
        mock = Mock(side_effect=doc_text)
        monkeypatch.setattr(BaseS3Client, "read_object", mock)

        focus_ther_tag = simple_therapy_tag(focus=True)
        ther_tag = simple_therapy_tag(focus=False)
        lost_ther_tag = simple_therapy_tag(focus=False)
        focus_indi_tag = simple_indication_tag(focus=True)
        indi_tag = simple_indication_tag(focus=False)
        lost_indi_tag = simple_indication_tag(focus=False)
        ret_doc = await simple_ret_doc(
            site=site, therapy_tags=[ther_tag], indication_tags=[indi_tag]
        ).save()
        doc_doc = await simple_doc_doc(
            site=site,
            retrieved_doc=ret_doc,
            therapy_tags=[focus_ther_tag, ther_tag, lost_ther_tag],
            indication_tags=[indi_tag, focus_indi_tag, lost_indi_tag],
        ).save()

        therapy_tags, indication_tags = await tag_compare.execute(ret_doc, doc_doc)
        assert len(therapy_tags) == 4
        assert len(indication_tags) == 4

        group_tags = group_by_status(therapy_tags)
        assert len(group_tags[TagUpdateStatus.REMOVED]) == 3
        assert len(group_tags["None"]) == 1
        assert group_tags["None"][0].code == ther_tag.code

        group_tags = group_by_status(indication_tags)
        assert len(group_tags[TagUpdateStatus.REMOVED]) == 3
        assert len(group_tags["None"]) == 1
        assert group_tags["None"][0].code == indi_tag.code

    @pytest.mark.asyncio
    async def test_removed_tag(
        self,
        mock_s3_client,  # noqa
        monkeypatch: pytest.MonkeyPatch,
        tag_compare: TagCompare,
        site: Site,
    ):
        doc_text = [bytes("string two", "utf-8"), bytes("string two", "utf-8")]
        mock = Mock(side_effect=doc_text)
        monkeypatch.setattr(BaseS3Client, "read_object", mock)

        tag_one = simple_therapy_tag(focus=True, text_area=(0, 20))
        tag_two = simple_therapy_tag(focus=True, text_area=(0, 20))
        ret_doc = await simple_ret_doc(site=site, therapy_tags=[tag_one]).save()
        doc_doc = await simple_doc_doc(
            site=site, retrieved_doc=ret_doc, therapy_tags=[tag_one, tag_two]
        ).save()

        therapy_tags, _ = await tag_compare.execute(ret_doc, doc_doc)
        assert len(therapy_tags) == 3
        removed_tags = group_by_status(therapy_tags)[TagUpdateStatus.REMOVED]
        assert len(removed_tags) == 2
        added_tags = group_by_status(therapy_tags)[TagUpdateStatus.ADDED]
        assert len(added_tags) == 1
        assert added_tags[0].code == tag_one.code

    def test_id_tag_compare(self):
        """Regardless of section status,
        if ID tags have been addded/removed mark tags accordingly"""
        ther_tag1 = simple_therapy_tag()
        ther_tag2 = simple_therapy_tag()
        ther_tag3 = simple_therapy_tag()
        a_section = DocumentSection(
            text_area=(0, 20), key_text="Key Text", id_tags=[ther_tag1, ther_tag3], ref_tags=[]
        )
        b_section = DocumentSection(
            text_area=(0, 20), key_text="Key Text", id_tags=[ther_tag1, ther_tag2], ref_tags=[]
        )

        section = SectionLineage(a_section, b_section)
        section.compare_id_tags()

        assert len(a_section.id_tags) == 3
        assert a_section.id_tags[2].update_status == TagUpdateStatus.REMOVED
        assert a_section.id_tags[1].update_status == TagUpdateStatus.ADDED
        assert a_section.id_tags[0].update_status is None

    async def test_ref_tag_changes(
        self,
        mock_s3_client,  # noqa
        monkeypatch: pytest.MonkeyPatch,
        tag_compare: TagCompare,
        site: Site,
    ):
        doc_text = [bytes("string one", "utf-8"), bytes("string two", "utf-8")]
        mock = Mock(side_effect=doc_text)
        monkeypatch.setattr(BaseS3Client, "read_object", mock)

        ther_one = simple_therapy_tag(focus=True, text_area=(0, 20))
        ther_ref_changed = simple_therapy_tag(focus=False, text_area=(0, 20))
        ther_ref_added = simple_therapy_tag(focus=False, text_area=(0, 20))
        indi_one = simple_indication_tag(focus=True, text_area=(0, 20))
        indi_ref_changed = simple_indication_tag(focus=False, text_area=(0, 20))
        indi_ref_added = simple_indication_tag(focus=False, text_area=(0, 20))
        ret_doc = await simple_ret_doc(
            site=site,
            therapy_tags=[ther_one, ther_ref_changed, ther_ref_added],
            indication_tags=[indi_one, indi_ref_added, indi_ref_changed],
        ).save()
        doc_doc = await simple_doc_doc(
            site=site,
            retrieved_doc=ret_doc,
            therapy_tags=[ther_one, ther_ref_changed],
            indication_tags=[indi_one, indi_ref_changed],
        ).save()

        therapy_tags, indication_tags = await tag_compare.execute(ret_doc, doc_doc)

        assert len(therapy_tags) == 3
        group_tags = group_by_status(therapy_tags)
        assert len(group_tags[TagUpdateStatus.ADDED]) == 1
        assert group_tags[TagUpdateStatus.ADDED][0].code == ther_ref_added.code
        assert len(group_tags[TagUpdateStatus.CHANGED]) == 2

        assert len(indication_tags) == 3
        group_tags = group_by_status(indication_tags)
        assert len(group_tags[TagUpdateStatus.ADDED]) == 1
        assert group_tags[TagUpdateStatus.ADDED][0].code == indi_ref_added.code
        assert len(group_tags[TagUpdateStatus.CHANGED]) == 2

    async def test_key_areas(
        self,
        mock_s3_client,  # noqa
        monkeypatch: pytest.MonkeyPatch,
        tag_compare: TagCompare,
        site: Site,
    ):
        doc_text = [bytes("string one", "utf-8"), bytes("string two", "utf-8")]
        mock = Mock(side_effect=doc_text)
        monkeypatch.setattr(BaseS3Client, "read_object", mock)

        key_ther = simple_therapy_tag(focus=True, text_area=(0, 20), key=True)
        focus_ther = simple_therapy_tag(focus=False, text_area=(0, 20))
        ret_doc = await simple_ret_doc(
            site=site,
            therapy_tags=[key_ther, focus_ther],
        ).save()
        doc_doc = await simple_doc_doc(
            site=site,
            retrieved_doc=ret_doc,
            therapy_tags=[focus_ther],
        ).save()

        therapy_tags, indication_tags = await tag_compare.execute(ret_doc, doc_doc)

        assert len(therapy_tags) == 2
        group_tags = group_by_status(therapy_tags)
        assert len(group_tags[TagUpdateStatus.ADDED]) == 2


class TestRefTags:
    def test_remove_ref_tag(self):
        ther_tag1 = simple_therapy_tag()
        ther_tag2 = simple_therapy_tag()
        a_section = DocumentSection(text_area=(0, 20), id_tags=[ther_tag1], ref_tags=[ther_tag1])
        b_section = DocumentSection(
            text_area=(0, 20), id_tags=[ther_tag1], ref_tags=[ther_tag1, ther_tag2]
        )

        section = SectionLineage(a_section, b_section)
        section.compare_ref_tags()

        removed_tag = ther_tag2
        removed_tag.update_status = TagUpdateStatus.REMOVED
        assert len(a_section.ref_tags) == 2
        assert a_section.ref_tags[1].update_status == TagUpdateStatus.REMOVED

    def test_no_remove_ref_tags(self):
        ther_tag1 = simple_therapy_tag()
        ther_tag2 = simple_therapy_tag()
        a_section = DocumentSection(
            text_area=(0, 20), id_tags=[ther_tag1], ref_tags=[ther_tag1, ther_tag2]
        )
        b_section = DocumentSection(
            text_area=(0, 20), id_tags=[ther_tag1], ref_tags=[ther_tag1, ther_tag2]
        )

        section = SectionLineage(a_section, b_section)
        section.compare_ref_tags()

        assert a_section.ref_tags == [ther_tag1, ther_tag2]
        assert len(a_section.ref_tags) == 2
        for tag in a_section.ref_tags:
            assert tag.update_status is None

    async def test_remove_tag(
        self,
        mock_s3_client,  # noqa
        monkeypatch: pytest.MonkeyPatch,
        tag_compare: TagCompare,
        site: Site,
    ):
        doc_text = [bytes("string one", "utf-8"), bytes("string two", "utf-8")]
        mock = Mock(side_effect=doc_text)
        monkeypatch.setattr(BaseS3Client, "read_object", mock)

        ther_one = simple_therapy_tag(focus=True, text_area=(0, 20))
        ther_one.update_status = TagUpdateStatus.ADDED
        ther_two = simple_therapy_tag(focus=True, text_area=(0, 20))

        ret_doc = await simple_ret_doc(
            site=site,
            therapy_tags=[ther_two],
        ).save()
        doc_doc = await simple_doc_doc(
            site=site,
            retrieved_doc=ret_doc,
            therapy_tags=[ther_one],
        ).save()

        therapy_tags, _ = await tag_compare.execute(ret_doc, doc_doc)
        group_tags = group_by_status(therapy_tags)
        assert len(group_tags[TagUpdateStatus.REMOVED]) == 1
