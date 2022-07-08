import logging
from redis import Redis
from backend.common.core.config import config,is_local
from urllib.parse import urlparse

# a connection redis helper
def redis_connect():
    logging.info(f'connecting to redis')
    parsed = urlparse(config['REDIS_URL'])

    client = Redis(
        host=parsed.hostname,
        port=parsed.port or 6379,
        username="default",
        password=config['REDIS_PASSWORD'],
        ssl=bool(not is_local),
    )

    client.ping()
    logging.info(f'connected to redis')
    return client
