import os
from datetime import datetime
from random import random

import pytest_asyncio
from fitz import Document as fitzDocument

from backend.common.core.enums import ScrapeMethod
from backend.common.db.init import init_db
from backend.common.models.doc_document import DocDocument, DocDocumentLocation
from backend.common.models.document import RetrievedDocument, RetrievedDocumentLocation
from backend.common.models.site import ScrapeMethodConfiguration, Site
from backend.common.services.text_compare.diff_utilities import WordSpan
from backend.common.services.text_compare.doc_text_compare import CompareDoc
from backend.common.test.test_utils import mock_s3_client  # noqa

current_path = os.path.dirname(os.path.realpath(__file__))
a_name = os.path.join(current_path, "one")
b_name = os.path.join(current_path, "two")


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)


@pytest_asyncio.fixture(autouse=True)
async def site():
    site = await Site(
        name="Test",
        scrape_method=ScrapeMethod.Simple,
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


def simple_ret_doc(site: Site) -> RetrievedDocument:
    return RetrievedDocument(
        name="test",
        checksum=a_name,
        text_checksum="test",
        first_collected_date=datetime.now(),
        last_collected_date=datetime.now(),
        therapy_tags=[],
        indication_tags=[],
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


def simple_doc_doc(site: Site, retrieved_doc: RetrievedDocument):
    return DocDocument(
        name="test",
        retrieved_document_id=retrieved_doc.id,
        checksum=b_name,
        text_checksum="test",
        first_collected_date=datetime.now(),
        last_collected_date=datetime.now(),
        therapy_tags=[],
        indication_tags=[],
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


def get_test_pdf_path():
    current_path = os.path.dirname(os.path.realpath(__file__))
    a_path = os.path.join(current_path, "../__fixtures__/test_pdf.pdf")
    return a_path


def get_b_file():
    current_path = os.path.dirname(os.path.realpath(__file__))
    b_name = os.path.join(current_path, "two.pdf")
    with open(b_name, "rb") as file:
        doc = file.read()
    return doc


# @pytest.mark.asyncio
# async def test_create_docs(monkeypatch: MonkeyPatch, mock_s3_client, site: Site):  # noqa
#     ret_doc = await simple_ret_doc(site).save()
#     doc_doc = await simple_doc_doc(site, ret_doc).save()
#     # file1 = get_a_file()
#     # file2 = get_b_file()
#     # responses = [file1, file2]
#     # mock = Mock(side_effect=responses)
#     # monkeypatch.setattr(BaseS3Client, "read_object", mock)
#     dtc = DocTextCompare()
#     dtc.compare(ret_doc, doc_doc)


class TestCompareDoc:
    def test_set_clean_pages(self):
        pdf_path = get_test_pdf_path()
        compare_doc = CompareDoc(fitz_pdf_doc=fitzDocument(pdf_path))
        removed_words = [
            WordSpan(page_num=0, start=3, end=4),
            WordSpan(page_num=1, start=1, end=2),
        ]
        compare_doc.set_clean_pages(removed_words)
        expected_page_lens = [10, 5]
        for i, page in enumerate(compare_doc.clean_pages):
            assert len(page) == expected_page_lens[i]
        compare_doc.set_clean_text()
        assert (
            compare_doc.clean_text
            == "Test PDF line\nLine 2\nLine 3\nLonger line here\fPage\nLine 2 Page 2"
        )

    def test_page_word_offsets(self):
        pdf_path = get_test_pdf_path()
        compare_doc = CompareDoc(fitz_pdf_doc=fitzDocument(pdf_path))
        assert compare_doc.page_word_offsets == [0, 11]
        removed_words = [
            WordSpan(page_num=0, start=3, end=4),
            WordSpan(page_num=0, start=1, end=2),
        ]
        compare_doc.set_clean_pages(removed_words)
        assert compare_doc.clean_page_word_offsets == [0, 9]

    def test_words_to_lines(self):
        pdf_path = get_test_pdf_path()
        compare_doc = CompareDoc(fitz_pdf_doc=fitzDocument(pdf_path))
        words = compare_doc.pages[0]
        lines = compare_doc.words_to_lines(words)
        assert lines == ["Test PDF line 1", "Line 2", "Line 3", "Longer line here"]
