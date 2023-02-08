import pytest

from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.crawlers.search_crawler import SearchableCrawler


class MockLogger:
    pass


@pytest.fixture()
def crawler():
    search_crawler = SearchableCrawler(config=ScrapeMethodConfiguration(), log=MockLogger())

    return search_crawler


def test_get_prefix_codes(crawler: SearchableCrawler):
    search_codes = ["12", "123", "abba", "abbc", "abbbbbbb", "aaab", "abaaaa"]
    prefix_codes = crawler._get_prefix_codes(search_codes, prefix_length=3)
    assert len(prefix_codes) == 5
    assert prefix_codes == ["12", "123", "aaa", "aba", "abb"]
