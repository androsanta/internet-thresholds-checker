import logging

from apscheduler.schedulers.background import BackgroundScheduler

from internet_checker.web_cube_api import WebCubeApiException
from . import web_cube
from .database import database

logger = logging.getLogger(__name__)


def _reading_task():
    try:
        status = web_cube.get_status()
    except WebCubeApiException:
        logger.warning('WebCubeApiException, cannot get status')
    else:
        reading = status.get('reading')
        logger.info(f'WebCube status: {status}')
        if reading:
            database.save_reading(reading)
            logger.info(f'Reading: {reading.to_dict()}')


def _reboot_task():
    try:
        web_cube.reboot()
        logger.info('WebCube rebooted')
    except WebCubeApiException:
        logger.warning('WebCubeApiException, cannot reboot')


scheduler = BackgroundScheduler()
scheduler.add_job(_reading_task, 'cron', minute='10,30,50', hour='0,7-23')
scheduler.add_job(_reboot_task, 'cron', minute='5', hour='0')
