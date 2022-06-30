import logging
from playwright.async_api import Route, Request as RouteRequest
from backend.scrapeworker.strategies.playwright_strategies.base_strategy import (
    BaseStrategy,
)
from backend.scrapeworker.common.models import Download, Request


class WordPressAjaxStrategy(BaseStrategy):
    async def execute(self):
        downloads = []
        requests = []

        async def intercept(
            route: Route,
            request: RouteRequest,
        ):
            if "/wp-admin/admin-ajax.php" in request.url:
                print("intercept continue", request)
                requests.append(request)
            await route.continue_()

        await self.page.route("**/*", intercept)
        await self.nav_to_page()

        # need to use jq/jsonpath to look into JSON and get pdfs + metdata
        elements = await self.find_elements("a.nothing")
        logging.info(f"elementsLength={len(elements)}")
        for request in requests:
            downloads.append(
                Download(
                    metadata=None,
                    request=Request(
                        url=request.url,
                        headers=request.headers,
                    ),
                ),
            )

        logging.info(f"downloadsLength={len(downloads)}")

        await self.page.unroute("**/*", intercept)

        return (elements, downloads)
