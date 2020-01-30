import json
import logging
from datetime import datetime

from flask import Flask, abort

from . import web_cube
from .database import database
from .scheduler import scheduler
from .web_cube_api import WebCubeApiException

app = Flask(__name__)
scheduler.start()
logging.basicConfig(level=logging.INFO)


@app.route('/weekly_readings', methods=['GET'])
def get_weekly_readings():
    weekly_readings = database.get_weekly_readings(datetime.now())
    weekly_readings['readings'] = list(map(lambda r: r.to_dict(), weekly_readings['readings']))
    return json.dumps(weekly_readings)


@app.route('/status', methods=['GET'])
def get_remaining_data():
    try:
        status = web_cube.get_status()
        reading = status.get('reading')
        if not reading:
            status['reading'] = database.get_last_reading()

        status['reading'] = status['reading'].to_dict()
        return json.dumps(status)
    except WebCubeApiException:
        abort(status=500)
