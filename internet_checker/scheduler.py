import logging

from apscheduler.schedulers.background import BackgroundScheduler

from . import web_cube
from .database import database

logger = logging.getLogger(__name__)


def _task():
    status = web_cube.get_status()
    reading = status.get('reading')
    logger.info(f'WebCube status: {status}')
    if reading:
        database.save_reading(reading)
        logger.info(f'Reading: {reading.to_dict()}')


scheduler = BackgroundScheduler()
scheduler.add_job(_task, 'cron', minute='10,30,50', hour='0,7-23')
