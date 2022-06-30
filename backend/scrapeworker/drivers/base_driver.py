import logging
from random import shuffle
from typing import Any
from backend.common.models.proxy import Proxy
from backend.scrapeworker.common.rate_limiter import RateLimiter


class BaseDriver:
    def __init__(self):
        self.rate_limiter = RateLimiter()

    def convert_proxy(self, proxy: Proxy) -> Any:
        pass

    def convert_proxies(self, proxies: list[Proxy]) -> list[any]:
        proxy_list = [self.convert_proxy(proxy) for proxy in proxies]
        shuffle(proxy_list)
        return proxy_list

    async def proxy_with_backoff(self, proxies: list[Proxy] = []):
        async for attempt in self.rate_limiter.attempt_with_backoff(3):
            i = attempt.retry_state.attempt_number - 1
            proxy_count = len(proxies)
            proxy, proxy_config = (
                proxies[i % proxy_count] if proxy_count > 0 else [None, None]
            )
            if proxy and proxy_config:
                logging.info(
                    f"{i} Using proxy {proxy and proxy.name} ({proxy_config and proxy_config['proxy']})"
                )

            yield attempt, proxy_config

    @property
    def closest_heading_expression(self):
        return """
            (node) => {
                let n = node;
                while (n) {
                    const h = n.querySelector('h1, h2, h3, h4, h5, h6, label')
                    if (h) return h.textContent;
                    n = n.parentNode;
                }
            }
        """
