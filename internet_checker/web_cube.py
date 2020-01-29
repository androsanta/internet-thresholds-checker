import logging
import time
from datetime import datetime

from .config import config
from .database import Reading
from .web_cube_api import web_cube_api, WebCubeApiException

logger = logging.getLogger(__name__)
_threshold = config['DISCONNECT_THRESHOLD']
_daily_threshold = config['DAILY_THRESHOLD']

_connection_enabled = None
_traffic_exceeded = None


def _set_connection_enabled(enabled: bool):
    global _connection_enabled

    if enabled == _connection_enabled:
        status = 'ON' if enabled else 'OFF'
        logger.info(f'Mobile connection already {status}')
        return

    web_cube_api.set_mobile_connection(enabled)
    _connection_enabled = enabled

    status = 'ENABLED' if enabled else 'DISABLED'
    logger.info(f'Mobile connection set to {status}')


def _get_reading():
    remaining_data = web_cube_api.get_remaining_data()
    return Reading(remaining_data['remaining_gb'], remaining_data['total_gb'])


def get_status():
    global _connection_enabled
    global _traffic_exceeded

    if _connection_enabled is None or not _connection_enabled and not _traffic_exceeded:
        # local information are not up to date
        logger.info('Local WebCube information are not up to date')
        try:
            enabled = web_cube_api.get_mobile_connection()
        except WebCubeApiException:
            _connection_enabled = None
            _traffic_exceeded = None
            logger.info('WebCube cannot be reached')
        else:
            _connection_enabled = enabled
            if not _connection_enabled:
                _set_connection_enabled(True)
                time.sleep(5)
            logger.info('Local WebCube information updated, connection reset to ENABLED')

    reading = None
    if _connection_enabled:
        reading = _get_reading()

    now = datetime.now()
    if now.hour >= 8:  # daytime
        if reading:
            daily_traffic_exceeded = reading.daily_traffic_left_gb < _daily_threshold and reading.days_to_renew > 1
            threshold_exceeded = reading.percentage <= _threshold
            if daily_traffic_exceeded or threshold_exceeded:
                _set_connection_enabled(False)
                _traffic_exceeded = True
                logger.info('Traffic exceeded')
    else:  # nighttime
        _set_connection_enabled(True)
        _traffic_exceeded = False

    return {
        'reading': reading,
        'connected': _connection_enabled,
        'trafficExceeded': _traffic_exceeded
    }


def reboot():
    web_cube_api.reboot()
