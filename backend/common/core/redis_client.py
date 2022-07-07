import logging
from redis import Redis
from backend.common.core.config import config
from urllib.parse import urlparse

# a connection redis helper
def redis_connect():
    logging.debug(f'connecting to redis')
    parsed = urlparse(config['REDIS_URL'])
    client = Redis(
        host=parsed.hostname,
        port=parsed.port,
        username="default",
        password=config['REDIS_PASSWORD'],
        ssl=True,
    )
    logging.debug(f'connected to redis')
    return client
