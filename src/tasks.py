import logging
from datetime import datetime

from src.database import Reading, database
from src.web_cube import web_cube, WebCubeException

logger = logging.getLogger(__name__)


def check_threshold(threshold_percent: int = 15):
    logger.info(f'\nSTART Background task execution - {datetime.now()}')

    now = datetime.now()

    try:
        if now.hour >= 8:  # daytime
            if web_cube.connection_enabled:
                logger.info('getting remaining data')
                reading: Reading = web_cube.get_remaining_data()
                logger.info('getting remaining data end')

                logger.info(f'Reading: {reading.to_dict()}')
                database.save_reading(reading)

                daily_traffic_exceeded = reading.daily_traffic_left_gb < 0.7 and reading.days_to_renew > 1
                threshold_exceeded = reading.percentage <= threshold_percent

                if daily_traffic_exceeded or threshold_exceeded:
                    web_cube.connection_enabled = False
                    logger.info('Traffic usage exceeded, disabling WebCube connection')

        else:  # nighttime
            if not web_cube.connection_enabled:
                web_cube.connection_enabled = True

    except WebCubeException as e:
        logger.warning('An error occurred during background task')

    logger.info(f'END Background task execution - {datetime.now()}\n')
