import re
from urllib.parse import parse_qsl

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper

# GET /Coverage/{siteCode}/Drug/{drugId}


# FORMULARY_NAVIGATOR_URL=https://api.formularynavigator.com
# for now because no api key ...
# FORMULARY_NAVIGATOR_USERNAME=
# FORMULARY_NAVIGATOR_PASSWORD=
# but eventually...?
# FORMULARY_NAVIGATOR_API_KEY=


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

    async def is_applicable(self) -> bool:
        self.log.debug(f"self.parsed_url.netloc={self.parsed_url.netloc}")
        result = self.parsed_url.netloc in ["client.formularynavigator.com"]
        self.log.info(f"{self.__class__.__name__} is_applicable -> {result}")
        return result

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []

        token_result = await self._get_access_token("", "")

        if token := token_result and token_result.get("accessToken", None):
            self.token = token
            self.headers["Authorization"] = f"Bearer {self.token}"
        else:
            raise Exception("Failed auth")

        result = await self._get_drug_coverage(self.site_code, "202537")
        href_regex = re.compile(r"https://fm.formularynavigator.com", re.IGNORECASE)

        # TODO less nested tomfoolery...
        for coverage in result["coverages"]:
            for fields in coverage["coverageDataFields"]:
                soup = BeautifulSoup(f"<div>{fields['details']}</div>", features="html.parser")
                for anchor in soup.find_all(attrs={"href": href_regex}):
                    downloads.append(
                        DownloadContext(
                            metadata=Metadata(link_text=coverage["drugName"]),
                            request=Request(url=anchor["href"]),
                        )
                    )
        return downloads

    async def _get_access_token(self, username: str, password: str) -> str | None:
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

    async def _get_drug_coverage(self, site_code: str, drug_id: str) -> str | None:
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
