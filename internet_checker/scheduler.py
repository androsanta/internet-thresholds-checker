import logging
from dataclasses import asdict

from apscheduler.schedulers.background import BackgroundScheduler

from . import web_cube
from .database import database

logger = logging.getLogger(__name__)


def _reading_task():
    try:
        logger.info('Getting status')
        status = web_cube.get_status()
        logger.info(f'WebCube status: {status}')
    except:
        logger.warning('WebCubeApiException, cannot get status')
    else:
        if status.reading:
            logger.info('Saving reading')
            database.save_reading(status.reading)
            logger.info('Reading saved')
            logger.info(f'Reading: {asdict(status.reading)}')


def _reboot_task():
    try:
        logger.info('Rebooting WebCube')
        web_cube.reboot()
        logger.info('WebCube rebooted')
    except:
        logger.warning('WebCubeApiException, cannot reboot')


scheduler = BackgroundScheduler()
scheduler.add_job(_reading_task, 'cron', minute='10,30,50', hour='0,7-23')
scheduler.add_job(_reboot_task, 'cron', minute='5', hour='0')
