from random import shuffle
from tenacity._asyncio import AsyncRetrying
from tenacity.stop import stop_after_attempt

class BaseDriver:
    async def navigate():
        pass

    async def find():
        pass

    async def collect():
        pass


async def try_each_proxy(self):
    """
        Try each proxy in turn, if it fails, try the next one. Repeat a few times for good measure.
        """
    proxy_settings = await self.get_proxy_settings()
    shuffle(proxy_settings)
    n_proxies = len(proxy_settings)
    async for attempt in AsyncRetrying(stop=stop_after_attempt(3*n_proxies)):
        i = attempt.retry_state.attempt_number - 1
        proxy, proxy_setting = proxy_settings[i % n_proxies]
        print(
            f"{i} Trying proxy {proxy and proxy.name} - {proxy_setting and proxy_setting.get('server')}")
        yield attempt, proxy_setting
