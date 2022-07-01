from backend.scrapeworker.strategies.playwright_strategies.aspnet_webform import (
    AspNetWebFormStrategy,
)

from backend.scrapeworker.strategies.playwright_strategies.direct_download import (
    DirectDownloadStrategy,
)

strategies = [AspNetWebFormStrategy, DirectDownloadStrategy]
