import logging
import time
from datetime import datetime

from . import web_cube_api
from .config import config
from .models import Status

logger = logging.getLogger(__name__)
_threshold = config['DISCONNECT_THRESHOLD']
_daily_threshold = config['DAILY_THRESHOLD']

_connection_enabled = None
_traffic_exceeded = False


def _set_mobile_connection(enabled: bool):
    global _connection_enabled
    # update info anyway
    _connection_enabled = web_cube_api.get_mobile_connection()

    if enabled == _connection_enabled:
        logger.info(f'Mobile connection already set to {enabled}')
        return

    web_cube_api.set_mobile_connection(enabled)
    _connection_enabled = enabled

    logger.info(f'Mobile connection set to {enabled}')


def get_status() -> Status:
    global _connection_enabled
    global _traffic_exceeded

    if _connection_enabled is None or not _connection_enabled and not _traffic_exceeded:
        # missing local information, get it
        logger.info('Local WebCube information are not up to date')
        try:
            _set_mobile_connection(True)
            time.sleep(5)
            logger.info('Local WebCube information updated, connection reset to ENABLED')
        except:
            _connection_enabled = None
            _traffic_exceeded = False
            logger.info('WebCube cannot be reached')

    reading = None
    if _connection_enabled:
        reading = web_cube_api.get_reading()

    now = datetime.now()
    if now.hour >= 8:  # daytime
        if reading:
            details = reading.get_detailed_status()
            daily_traffic_exceeded = details.mean_daily_left_gb < _daily_threshold and details.days_to_renew > 1
            threshold_exceeded = details.percentage <= _threshold
            if daily_traffic_exceeded or threshold_exceeded:
                _set_mobile_connection(False)
                _traffic_exceeded = True
                logger.info('Traffic exceeded')
    else:  # nighttime
        _set_mobile_connection(True)
        _traffic_exceeded = False

    return Status(reading, _connection_enabled, _traffic_exceeded)


def reboot():
    web_cube_api.reboot()
