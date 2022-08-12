# log, can get fancy, but is at all
import logging

from backend.app.core.settings import settings

log_level: str = settings.log_level
logging.basicConfig(level=getattr(logging, log_level.upper()))
