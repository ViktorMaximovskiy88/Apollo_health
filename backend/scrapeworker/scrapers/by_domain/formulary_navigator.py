import re
from urllib.parse import ParseResult, parse_qsl, urlparse

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from backend.app.core.settings import settings
from backend.common.models.search_codes import SearchCodeSet
from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class FormularyNavigatorScraper(PlaywrightBaseScraper):

    type: str = "FormularyNavigatorScraper"
    downloads: list[DownloadContext] = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "https://api.formularynavigator.com"
        self.token = None
        params = dict(parse_qsl(self.parsed_url.query))
        self.site_code = params.get("siteCode", None)
        self.headers = {
            "content-type": "application/json",
        }
        self.username = settings.formulary_navigator.formulary_navigator_username
        self.password = settings.formulary_navigator.formulary_navigator_password

    @staticmethod
    def scrape_select(url, config: ScrapeMethodConfiguration | None = None) -> bool:
        parsed_url: ParseResult = urlparse(url)
        result = parsed_url.netloc == "client.formularynavigator.com"
        return result

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []

        token_result = await self._get_access_token(self.username, self.password)

        if token := token_result and token_result.get("accessToken", None):
            self.token = token
            self.headers["Authorization"] = f"Bearer {self.token}"
        else:
            raise Exception("Failed auth")

        tokens = await SearchCodeSet.get_universal_tokens()
        for token in tokens:
            token = f"{token}".lower().strip()
            if not token:
                continue

            drug_result = await self._get_drug_search(self.site_code, token)

            if drug_result.get("error", None):
                self.log.error(f"{drug_result['error']}")
                continue

            if not drug_result.get("drugs", None):
                self.log.warn(f"no drugs for token={token}")
                continue

            for drug in drug_result["drugs"]:
                drug_id = drug["drugId"]
                coverage_result = await self._get_drug_coverage(self.site_code, drug_id)
                href_regex = re.compile(r"https://fm\.formularynavigator\.com", re.IGNORECASE)

                if coverage_result.get("error", None):
                    self.log.error(f"{coverage_result['error']}")
                    continue

                if not coverage_result.get("coverages", None):
                    self.log.error(f"no coverages for drug_id={drug_id}")
                    continue

                for coverage in coverage_result["coverages"]:
                    for fields in coverage["coverageDataFields"]:
                        soup = BeautifulSoup(
                            f"<div>{fields['details']}</div>", features="html.parser"
                        )
                        for anchor in soup.find_all(attrs={"href": href_regex}):
                            downloads.append(
                                DownloadContext(
                                    metadata=Metadata(link_text=coverage["drugName"]),
                                    request=Request(url=anchor["href"]),
                                )
                            )

        return downloads

    async def _get_access_token(self, username: str, password: str) -> dict:
        url = f"{self.api_url}/User/Token"
        data = {"loginID": username, "password": password}
        result = await self._request(
            url,
            method="POST",
            data=data,
            headers={
                "Accept": "*/*",
            },
        )
        return result

    async def _get_drug_search(self, site_code: str, token: str) -> dict:
        url = f"{self.api_url}/Drugs/{site_code}/Name/{token}"
        result = await self._request(url)
        return result

    async def _get_drug_coverage(self, site_code: str, drug_id: str) -> dict:
        url = f"{self.api_url}/Coverage/{site_code}/Drug/{drug_id}"
        result = await self._request(url)
        return result

    async def _request(
        self,
        url: str,
        method: str = "GET",
        params: dict | None = None,
        data: dict | None = None,
        cookies: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
        async with ClientSession() as session:
            async with session.request(
                url=url,
                method=method,
                headers=headers or self.headers,
                json=data,
                cookies=cookies,
                params=params,
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(response)
