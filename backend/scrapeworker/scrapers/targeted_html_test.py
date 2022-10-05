from unittest.mock import MagicMock

import pytest
from playwright.async_api import BrowserContext, Page

from backend.common.models.site import AttrSelector, ScrapeMethodConfiguration
from backend.common.test.test_utils import mock_s3_client  # noqa
from backend.scrapeworker.scrapers.targeted_html import TargetedHtmlScraper


def simple_scrape_config():
    return ScrapeMethodConfiguration(
        document_extensions=[],
        url_keywords=[],
        proxy_exclusions=[],
        follow_links=False,
        follow_link_keywords=[],
        follow_link_url_keywords=[],
        html_exclusion_selectors=[
            AttrSelector(
                attr_element="div",
                attr_name="delete_me",
            ),
            AttrSelector(
                attr_element="span",
                attr_name="delete",
                attr_value="me",
            ),
        ],
    )


@pytest.fixture()
def scraper():
    html_scraper = TargetedHtmlScraper(
        MagicMock(spec=BrowserContext),
        MagicMock(spec=Page),
        "https://www.example.com",
        simple_scrape_config(),
    )

    return html_scraper


def test_clean_html(mock_s3_client, scraper: TargetedHtmlScraper):  # noqa
    test_html = "<html><body><div>not me</div></body></html>"

    html = '<div delete_me="test"></div><div>not me</div>'
    clean_html = scraper.clean_html(html)
    assert test_html == clean_html

    html = '<html><div delete_me="test"></div><div>not me</div></html>'
    clean_html = scraper.clean_html(html)
    assert test_html == clean_html

    html = '<html><body><div delete_me="test"></div><div>not me</div></body></html>'
    clean_html = scraper.clean_html(html)
    assert test_html == clean_html


def test_multiple_delete_clean_html(mock_s3_client, scraper: TargetedHtmlScraper):  # noqa
    test_html = "<html><body><div><div>not me</div></div></body></html>"

    html = '<div><span delete="me">byebye</span><div delete_me="test"></div><div>not me</div></div>'
    clean_html = scraper.clean_html(html)
    assert test_html == clean_html
