import json
import logging
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, abort

from src import tasks
from src.database import database
from src.web_cube import web_cube, WebCubeException

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

config = {
    'web_cube_username': os.environ['USERNAME'],
    'web_cube_password': os.environ['PASSWORD'],
    'db_host': os.environ['DATABASE'] if os.environ['DATABASE'] else 'localhost'
}


@app.route('/')
def entry_point():
    weekly_readings = database.get_weekly_readings(datetime.now())
    weekly_readings['readings'] = list(map(lambda r: r.to_dict(), weekly_readings['readings']))
    return render_template('index.html', data=json.dumps(weekly_readings))


@app.route('/remaining_data')
def get_remaining_data():
    try:
        if not web_cube.connection_enabled:
            return "Not connected"  # todo
        return json.dumps(web_cube.get_remaining_data().to_dict())
    except WebCubeException:
        abort(status=500)


scheduler = BackgroundScheduler()
scheduler.add_job(tasks.check_threshold, 'cron', minute='10,30,50', hour='0,7-23')
scheduler.start()

if __name__ == '__main__':
    app.run()
