import logging
from urllib.parse import urlparse, urljoin
from random import shuffle
from typing import Callable
from backend.common.models.proxy import Proxy
from backend.scrapeworker.common.rate_limiter import RateLimiter

# TODO these seem redundant but theres some extra checking to be had
# ill show the case later...
def parse_url(url: str):
    return urlparse(url)


def join_url(base, url):
    return urljoin(base, url)


def convert_proxies(
    proxies: list[Proxy],
    converter: Callable,
) -> list[any]:
    proxy_list = [converter(proxy) for proxy in proxies]
    shuffle(proxy_list)
    return proxy_list


async def proxy_with_backoff(
    proxies: [],
):
    rate_limiter = RateLimiter()
    async for attempt in rate_limiter.attempt_with_backoff(3):
        i = attempt.retry_state.attempt_number - 1
        proxy_count = len(proxies)
        proxy, proxy_config = (
            proxies[i % proxy_count] if proxy_count > 0 else [None, None]
        )
        if proxy and proxy_config:
            logging.info(f"{i} Using proxy {proxy and proxy.name})")

        yield attempt, proxy_config


closest_heading_expression: str = """
    (node) => {
        let n = node;
        while (n) {
            const h = n.querySelector('h1, h2, h3, h4, h5, h6, label')
            if (h) return h.textContent;
            n = n.parentNode;
        }
    }
"""
