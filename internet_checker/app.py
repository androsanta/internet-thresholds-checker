import json
import logging

from flask import Flask, make_response

from . import web_cube
from .database import database, my_asdict
from .models import StatusResponse
from .scheduler import scheduler
from .web_cube import Status

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
scheduler.start()


@app.route('/weekly_readings', methods=['GET'])
def get_weekly_readings():
    weekly_readings = database.get_weekly_readings()
    return json.dumps(my_asdict(weekly_readings))


@app.route('/status', methods=['GET'])
def get_remaining_data():
    try:
        status: Status = web_cube.get_status()
        details = status.reading.get_detailed_status() if status.reading else None
        return json.dumps(my_asdict(StatusResponse(status, details)))
    except Exception as e:
        print(e)
        return make_response(json.dumps({'message': str(e)}), 500)
