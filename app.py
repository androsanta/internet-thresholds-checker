import json

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template

from src import tasks

app = Flask(__name__)


# def get_week_threshold():
#     now = datetime.utcnow()
#     start_of_day = datetime(now.year, now.month, now.day)
#     start_day_of_week = start_of_day - timedelta(days=now.isoweekday())
#     end_day_of_week = start_day_of_week + timedelta(days=6)
#
#     pass


@app.route('/')
def entry_point():
    # todo fetch data from db
    data = [12, 19, 3, 5, 2, 3]
    return render_template('index.html', data=json.dumps(data))


scheduler = BackgroundScheduler()
scheduler.add_job(tasks.check_threshold, 'cron', minute='10,30,50', hour='8-23')
scheduler.start()

if __name__ == '__main__':
    app.run()
