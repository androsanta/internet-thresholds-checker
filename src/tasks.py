from datetime import datetime

from src import web_cube


def check_threshold(threshold_percent: int = 10):
    print(f'Background task execution - {datetime.now()} - utc time: {datetime.utcnow()}')
    remaining_data = web_cube.get_remaining_data()

    remaining = remaining_data['remaining']
    total = remaining_data['total']
    # todo save to db
    # database.save_reading(Reading(remaining, total))

    if remaining / total * 100 <= threshold_percent:
        # todo disconnect all devices
        pass
