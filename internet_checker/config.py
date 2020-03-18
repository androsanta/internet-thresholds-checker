import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

config = {
    'USERNAME': os.getenv('USERNAME'),
    'PASSWORD': os.getenv('PASSWORD'),
    'MOBILE_NUMBER': os.getenv('MOBILE_NUMBER'),
    'DATABASE_HOST': os.getenv('DATABASE_HOST', 'localhost'),
    'DISCONNECT_THRESHOLD': os.getenv('DISCONNECT_THRESHOLD', 5),
    'DAILY_THRESHOLD': os.getenv('DAILY_THRESHOLD', 0.9)
}

not_set = list(filter(lambda k: config[k] is None, config.keys()))
if len(not_set) > 0:
    msg = 'This environment variables must be set: ' + ', '.join(not_set)
    logger.error(msg)
    exit(1)
