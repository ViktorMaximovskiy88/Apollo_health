import logging
import sys

import json_logging
from fastapi import FastAPI


# TODO reintroduce user ... once i verify newrelic likes this...
def http_logger(app: FastAPI, log_level: str = "INFO"):
    json_logging.init_fastapi(enable_json=True)
    json_logging.init_request_instrument(app)

    _log_level = logging.getLevelName(log_level.upper())

    logger = logging.getLogger()
    logger.setLevel(_log_level)
    logger.addHandler(logging.StreamHandler(sys.stdout))
