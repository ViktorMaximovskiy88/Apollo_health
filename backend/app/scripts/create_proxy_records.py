import asyncio
from backend.app.utils.logger import Logger, create_and_log, update_and_log_diff

from backend.common.db.init import init_db
from backend.common.models.proxy import Proxy, ProxyCredentials
from backend.common.models.user import User

async def get_user() -> User:
    user = await User.by_email("admin@mmitnetwork.com")
    if not user:
        raise Exception("Admin user not found")
    return user

async def create_proxies():
    logger = Logger()
    user = await get_user()
    existing_proxies = await Proxy.find_all().to_list()
    old_proxies_by_name = { proxy.name: proxy for proxy in existing_proxies }
    proxies = [
        Proxy(name="Smart Proxy", endpoints=[
            "gate.dc.smartproxy.com:20000"
        ], credentials=ProxyCredentials(
            username_env_var='SMARTPROXY_USERNAME',
            password_env_var='SMARTPROXY_PASSWORD'
        )),
        Proxy(name="Proxy Mesh", endpoints=[
            "us-wa.proxymesh.com:31280",
            "us-il.proxymesh.com:31280",
            "us.proxymesh.com:31280",
            "us-dc.proxymesh.com:31280",
            "us-ca.proxymesh.com:31280",
            "us-ny.proxymesh.com:31280",
            "us-fl.proxymesh.com:31280",
        ]),
        Proxy(name="Trusted Proxy", endpoints=[
            "cld-us-wxda.tp-ns.com:80",
            "cld-us-ektv.tp-ns.com:80"
        ]),
    ]

    for proxy in proxies:
        old_proxy = old_proxies_by_name.pop(proxy.name, None)
        if old_proxy:
            await update_and_log_diff(logger, user, old_proxy, proxy)
        else:
            await create_and_log(logger, user, proxy)

    for old_proxy in old_proxies_by_name.values():
        await old_proxy.delete()
    pass

async def execute():
    await init_db()
    await create_proxies()


if __name__ == "__main__":
    asyncio.run(execute())
