from datetime import datetime
from random import random

import pytest
import pytest_asyncio

from backend.common.core.enums import DocumentType, SectionType
from backend.common.db.init import init_db
from backend.common.models.document import RetrievedDocument, RetrievedDocumentLocation
from backend.common.models.site import FocusSectionConfig, ScrapeMethodConfiguration, Site
from backend.scrapeworker.document_tagging.tag_focusing import FocusArea, FocusState
from backend.scrapeworker.document_tagging.therapy_tagging import FocusChecker


@pytest_asyncio.fixture()
async def new_db():
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)


class MockSpan:
    def __init__(self, text: str, start_char: int, end_char: int) -> None:
        self.text = text
        self.start_char = start_char
        self.end_char = end_char


def simple_focus_config():
    return FocusSectionConfig(
        section_type=[SectionType.INDICATION, SectionType.THERAPY],
        doc_type="Formulary",
        start_separator="Prior Authorization",
        end_separator="PA Indication",
        all_focus=False,
    )


def simple_ret_doc(site1: Site, site2: Site) -> RetrievedDocument:
    return RetrievedDocument(
        name="test",
        checksum="test",
        text_checksum="test",
        document_type="Formulary",
        first_collected_date=datetime.now(),
        last_collected_date=datetime.now(),
        locations=[
            RetrievedDocumentLocation(
                site_id=site1.id,
                first_collected_date=datetime.now(),
                last_collected_date=datetime.now(),
                url="https://www.example.com/doc",
                base_url="https://www.example.com/",
                link_text="",
                closest_heading="",
                siblings_text=None,
            ),
            RetrievedDocumentLocation(
                site_id=site2.id,
                first_collected_date=datetime.now(),
                last_collected_date=datetime.now(),
                url="https://www.example.com/doc",
                base_url="https://www.example.com/",
                link_text="",
                closest_heading="",
                siblings_text=None,
            ),
        ],
    )


async def simple_site(focus_configs: list[FocusSectionConfig] = []):
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
            focus_section_configs=focus_configs,
        ),
        disabled=False,
        cron="0 * * * *",
    ).save()
    return site


test_text = """
    Prior Authorization Group ACITRETIN
    Drug Names ACITRETIN
    PA Indication Indicator All FDA-approved Indications, Some Medically-accepted Indications
    Age Restrictions
    Prior Authorization Group ADAPALENE
    Drug Names ADAPALENE, DIFFERIN
    PA Indication Indicator All FDA-approved Indications
    Other Criteria - AUSTEDO
"""  # len() == 342


class TestFocusAreas:
    def test_get_focus_areas(self):
        url = "www.test.com"
        link_text = "test"
        config = simple_focus_config()
        focus_checker = FocusChecker(test_text, [config], url, link_text)
        assert focus_checker.focus_areas == [
            FocusArea(start=24, end=70, section_end=204),
            FocusArea(start=204, end=260, section_end=342),
        ]
        assert focus_checker.key_areas == []

    def test_key_focus_areas(self):
        url = "www.test.com"
        link_text = "test"
        config = simple_focus_config()
        config.section_type.append(SectionType.KEY)
        focus_checker = FocusChecker(test_text, [config], url, link_text)
        assert focus_checker.key_areas == [
            FocusArea(
                start=24,
                end=70,
                section_end=204,
                key_text=" Group ACITRETIN\n    Drug Names ACITRETIN\n    ",
            ),
            FocusArea(
                start=204,
                end=260,
                section_end=342,
                key_text=" Group ADAPALENE\n    Drug Names ADAPALENE, DIFFERIN\n    ",
            ),
        ]
        assert focus_checker.focus_areas == []

    def test_get_key_areas(self):
        url = "www.test.com"
        link_text = "test"
        config = simple_focus_config()
        focus_checker = FocusChecker(test_text, [config], url, link_text)
        assert focus_checker.key_areas == []

        config.section_type.append(SectionType.KEY)
        focus_checker = FocusChecker(test_text, [config], url, link_text)
        assert focus_checker.key_areas == [
            FocusArea(
                key_text=" Group ACITRETIN\n    Drug Names ACITRETIN\n    ",
                start=24,
                end=70,
                section_end=204,
            ),
            FocusArea(
                key_text=" Group ADAPALENE\n    Drug Names ADAPALENE, DIFFERIN\n    ",
                start=204,
                end=260,
                section_end=342,
            ),
        ]


class TestCheckFocus:
    def test_get_focus_by_area(self):
        url = "www.test.com"
        link_text = "test"
        config = simple_focus_config()
        focus_checker = FocusChecker(test_text, [config], url, link_text)

        focus_spans = [MockSpan("ACITRETIN", 30, 38), MockSpan("ADAPALENE", 236, 245)]
        focus_areas = focus_checker.focus_areas
        for i, span in enumerate(focus_spans):
            focus_state = focus_checker.check_focus(span, 0)
            section = focus_areas[i].end, focus_areas[i].section_end
            assert focus_state == FocusState(focus=True, key=False, section=section)

        non_focus_span = MockSpan("AUSTEDO", 330, 340)
        focus_state = focus_checker.check_focus(non_focus_span, 0)
        section = focus_areas[1].end, focus_areas[1].section_end
        assert focus_state == FocusState(focus=False, key=False, section=section)

    def test_get_focus_by_link(self):
        url = "www.test.com"
        link_text = "Download Acitretin Approval"
        config = simple_focus_config()
        focus_checker = FocusChecker(test_text, [config], url, link_text)
        focus_areas = focus_checker.focus_areas

        span = MockSpan("ACITRETIN", 300, 400)
        focus_state = focus_checker.check_focus(span, 0)
        section = focus_areas[1].end, focus_areas[1].section_end
        assert focus_state == FocusState(
            focus=True, key=False, section=section, is_in_link_text=True
        )

    def test_get_focus_by_url(self):
        url = "www.test.com/approval/acitretin-form-download"
        link_text = None
        config = simple_focus_config()
        focus_checker = FocusChecker(test_text, [config], url, link_text)
        focus_areas = focus_checker.focus_areas

        span = MockSpan("ACITRETIN", 330, 340)
        focus_state = focus_checker.check_focus(span, 0)
        section = focus_areas[1].end, focus_areas[1].section_end
        assert focus_state == FocusState(focus=True, key=False, section=section, is_in_url=True)

    def test_get_focus_by_all_focus(self):
        url = "www.test.com"
        link_text = "Download"
        config = simple_focus_config()
        config.all_focus = True
        focus_checker = FocusChecker(
            test_text,
            [config],
            url,
            link_text,
            DocumentType.Formulary,
        )
        focus_areas = focus_checker.focus_areas
        spans = [MockSpan("ACITRETIN", 330, 340), MockSpan("AUSTEDO", 250, 270)]
        for span in spans:
            focus_state = focus_checker.check_focus(span, 0)
            section = focus_areas[1].end, focus_areas[1].section_end
            assert focus_state == FocusState(focus=True, key=False, section=section)

    def test_no_start_separator(self):
        url = "www.test.com"
        link_text = "Download Austedo"
        config = simple_focus_config()
        config.start_separator = None
        focus_checker = FocusChecker(test_text, [config], url, link_text)

        span = MockSpan("ACITRETIN", 1, 10)
        focus_state = focus_checker.check_focus(span, 0)
        section = 70, 342
        assert focus_state == FocusState(focus=True, key=False, section=section)

    def test_no_end_separator(self):
        url = "www.test.com"
        link_text = "Download"
        config = simple_focus_config()
        config.end_separator = None
        focus_checker = FocusChecker(test_text, [config], url, link_text)

        spans = [MockSpan("AUSTEDO", 330, 341), MockSpan("ACITRETIN", 30, 38)]
        for span in spans:
            focus_state = focus_checker.check_focus(span, 0)
            section = 342, 342
            assert focus_state == FocusState(focus=True, key=False, section=section)

        non_focus_span = MockSpan("ACITRETIN", 1, 10)
        focus_state = focus_checker.check_focus(non_focus_span, 0)
        section = None
        assert focus_state == FocusState(focus=False, key=False, section=section)

    def test_multiple_configs(self):
        url = "www.test.com"
        link_text = "Download"
        config = simple_focus_config()
        config.start_separator = "Restrictions"
        config.end_separator = "Group"
        config_two = simple_focus_config()
        focus_checker = FocusChecker(test_text, [config, config_two], url, link_text)

        spans = [
            MockSpan("ACITRETIN", 30, 38),
            MockSpan("Authorization", 190, 200),
        ]
        focus_areas = focus_checker.focus_areas
        for i, span in enumerate(spans):
            focus_state = focus_checker.check_focus(span, 0)
            section = focus_areas[i].end, focus_areas[i].section_end
            assert focus_state == FocusState(focus=True, key=False, section=section)

    def test_get_no_focus_areas(self):
        url = "www.test.com"
        link_text = "Download"
        config = simple_focus_config()
        config.start_separator = "No Match"
        focus_checker = FocusChecker(test_text, [config], url, link_text)

        spans = [
            MockSpan("AUSTEDO", 330, 340),
            MockSpan("ACITRETIN", 30, 38),
            MockSpan("ACITRETIN", 1, 10),
        ]
        for span in spans:
            focus_state = focus_checker.check_focus(span, 0)
            assert focus_state == FocusState(
                focus=False, key=False, section=(span.start_char, span.end_char)
            )

    def test_no_config(self):
        url = "www.test.com"
        link_text = "Download Austedo"
        focus_checker = FocusChecker(test_text, [], url, link_text)

        span = MockSpan("AUSTEDO", 1000, 2000)
        focus_state = focus_checker.check_focus(span, 0)
        assert focus_state == FocusState(
            focus=True, key=False, section=(1000, 2000), is_in_link_text=True, is_in_url=False
        )

        non_focus_span = MockSpan("ACITRETIN", 30, 38)
        focus_state = focus_checker.check_focus(non_focus_span, 0)
        assert focus_state == FocusState(
            focus=False, key=False, section=(30, 38), is_in_link_text=False, is_in_url=False
        )

    def test_offset(self):
        # Test offset param in check_focus
        url = "www.test.com"
        link_text = "test"
        config = simple_focus_config()
        focus_checker = FocusChecker(test_text, [config], url, link_text)

        focus_spans = [MockSpan("ACITRETIN", 20, 28), MockSpan("ADAPALENE", 226, 235)]
        focus_areas = focus_checker.focus_areas
        for i, span in enumerate(focus_spans):
            focus_state = focus_checker.check_focus(span, 10)
            section = focus_areas[i].end, focus_areas[i].section_end
            assert focus_state == FocusState(focus=True, key=False, section=section)

        non_focus_span = MockSpan("AUSTEDO", 330, 340)
        focus_state = focus_checker.check_focus(non_focus_span, 10)
        section = focus_areas[1].end, focus_areas[1].section_end
        assert focus_state == FocusState(focus=False, key=False, section=section)

    def test_get_key_tag(self):
        url = "www.test.com"
        link_text = "test"
        config = simple_focus_config()
        config.start_separator = "Restrictions"
        config.end_separator = "Group"
        config2 = simple_focus_config()
        config2.section_type.append(SectionType.KEY)
        focus_checker = FocusChecker(test_text, [config, config2], url, link_text)

        key_span = MockSpan("ACITRETIN", 30, 38)
        focus_span = MockSpan("Authorization", 190, 200)
        key_areas = focus_checker.key_areas

        focus_state = focus_checker.check_focus(key_span, 0)
        section = key_areas[0].end, key_areas[0].section_end
        assert focus_state == FocusState(focus=True, key=True, section=section)

        focus_state = focus_checker.check_focus(focus_span, 0)
        section = key_areas[0].end, key_areas[0].section_end
        assert focus_state == FocusState(focus=True, key=False, section=section)

    def test_outside_focus_section(self):
        url = "www.test.com"
        link_text = "test"
        config = simple_focus_config()
        config.start_separator = "Restrictions"
        config.end_separator = "Group"
        config.section_type.append(SectionType.KEY)
        config2 = simple_focus_config()
        focus_checker = FocusChecker(test_text, [config, config2], url, link_text)

        focus_span = MockSpan("ACITRETIN", 30, 40)
        focus_state = focus_checker.check_focus(focus_span, 0)
        assert focus_state == FocusState(focus=True, key=False, section=None)

    @pytest.mark.asyncio
    async def test_location_focus_configs(self, new_db):
        config1 = simple_focus_config()
        config1.start_separator = "config1"
        config2 = simple_focus_config()
        config2.start_separator = "config2"
        config3 = simple_focus_config()
        config3.start_separator = "config3"

        site1 = await simple_site(focus_configs=[config1, config2])
        site2 = await simple_site(focus_configs=[config2, config3])
        doc = await simple_ret_doc(site1, site2).save()
        all_configs = await FocusChecker._location_focus_configs(
            doc, tag_type=SectionType.INDICATION
        )
        assert len(all_configs) == 3

        site1 = await simple_site(focus_configs=[config1])
        site2 = await simple_site(focus_configs=[config2])
        doc = await simple_ret_doc(site1, site2).save()
        all_configs = await FocusChecker._location_focus_configs(
            doc, tag_type=SectionType.INDICATION
        )
        assert len(all_configs) == 2

        site1 = await simple_site(focus_configs=[config1])
        site2 = await simple_site(focus_configs=[config1])
        doc = await simple_ret_doc(site1, site2).save()
        all_configs = await FocusChecker._location_focus_configs(
            doc, tag_type=SectionType.INDICATION
        )
        assert len(all_configs) == 1

        site1 = await simple_site()
        site2 = await simple_site()
        doc = await simple_ret_doc(site1, site2).save()
        all_configs = await FocusChecker._location_focus_configs(
            doc, tag_type=SectionType.INDICATION
        )
        assert len(all_configs) == 0
