import logging

from apscheduler.schedulers.background import BackgroundScheduler

from . import web_cube
from .database import database

logger = logging.getLogger(__name__)


def _task():
    status = web_cube.get_status()
    logger.info(f'WebCube status: {status}')
    reading = status.get('reading')
    if reading:
        database.save_reading(reading)


scheduler = BackgroundScheduler()
scheduler.add_job(_task, 'cron', minute='10,30,50', hour='0,7-23')
