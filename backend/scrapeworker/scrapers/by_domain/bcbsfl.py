from aiofiles import tempfile
from playwright.async_api import Error
from playwright.async_api import Request as RouteRequest
from playwright.async_api import Route, TimeoutError

from backend.common.storage.hash import hash_bytes
from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class BcbsflScraper(PlaywrightBaseScraper):

    type: str = "Bcbsfl"
    first_menu = '.rpRootGroup > .rpItem span.rpText:has-text("Current Guidelines")'
    second_menu = (
        '.rpRootGroup .rpGroup.rpLevel1 > .rpItem.rpLast span.rpText:has-text("Alphabetical")'
    )
    target_items = (
        ".rpRootGroup .rpGroup.rpLevel1 > .rpItem.rpLast .rpGroup.rpLevel2 > .rpItem span.rpText"
    )

    async def is_applicable(self) -> bool:
        self.log.debug(f"self.parsed_url.netloc={self.parsed_url.netloc}")
        result = self.parsed_url.netloc in ["mcgs.bcbsfl.com"]
        self.log.info(f"{self.__class__.__name__} is_applicable -> {result}")
        return result

    async def click_welcome_menu_elements(self):
        first_menu_el = await self.page.wait_for_selector(self.first_menu)
        await first_menu_el.click()
        second_menu_el = await self.page.wait_for_selector(self.second_menu)
        await second_menu_el.click()

    @staticmethod
    def is_postback(request):
        return "https://mcgs.bcbsfl.com/" == request.url and request.method == "POST"

    @staticmethod
    def is_frameload(request):
        return "https://mcgs.bcbsfl.com/mcg.aspx?FilePath=" in request.url

    @staticmethod
    async def intercept(route: Route, request: RouteRequest):
        if "FilePath" in request.url:
            await route.abort()
        else:
            await route.continue_()

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []

        await self.page.route("**/*", self.intercept)
        await self.click_welcome_menu_elements()

        text_locator = self.page.locator(self.target_items)
        link_texts = await text_locator.all_text_contents()
        for link_text in link_texts:
            link_locator = self.page.locator(
                f'.rpItem.rpLast .rpGroup.rpLevel2 > .rpItem .rpText:text-is("{link_text}")'
            )
            link_handle = await link_locator.element_handle()
            async with self.page.expect_request(self.is_postback):
                self.log.info(f"before target clicked link_text={link_text}")
                await link_handle.click()
                self.log.info(f"after target clicked link_text={link_text}")

                async with self.page.expect_request(self.is_frameload) as frame_load:
                    self.log.info(f"before frame_load link_text={link_text}")
                    request = await frame_load.value
                    self.log.info(f"after frame_load link_text={link_text}")

                    headers = await request.all_headers()
                    self.log.info(f"before fetch request.url={request.url}")
                    pdf_bytes = await self._fetch(request.url, headers=headers)
                    self.log.info(f"after fetch request.url={request.url} {len(pdf_bytes)}")

                    if not pdf_bytes:
                        continue

                    file_hash = hash_bytes(pdf_bytes)
                    async with tempfile.NamedTemporaryFile(delete=False) as file:
                        await file.write(pdf_bytes)
                        temp_path = file.name

                    downloads.append(
                        DownloadContext(
                            file_path=temp_path,
                            file_name=link_text,
                            playwright_download=True,
                            file_hash=file_hash,
                            metadata=Metadata(
                                link_text=link_text,
                                base_url=self.page.url,
                            ),
                            request=Request(
                                url=f"file://{temp_path}",
                                filename=link_text,
                            ),
                        ),
                    )

        await self.page.unroute("**/*", self.intercept)

        return downloads

    async def _fetch(
        self,
        url,
        method: str = "GET",
        headers: dict | None = None,
        data: dict | None = None,
        params: dict | None = None,
    ):
        try:
            response = await self.page.request.fetch(
                url,
                method=method,
                data=data,
                params=params,
                headers=headers,
                fail_on_status_code=True,
            )

            result = await response.body()
            await response.dispose()
            return result

        except TimeoutError as ex:
            self.log.error(f"data={data}", exc_info=ex)
        except Error as ex:
            self.log.error(f"data={data}", exc_info=ex)
        except Exception as ex:
            self.log.error(f"data={data}", exc_info=ex)
