from dataclasses import asdict
from datetime import datetime, timedelta

from pymongo import MongoClient

from .config import config
from .models import Reading, ReadingGroup


def _dict_factory_handle_date(fields):
    result = {}
    for name, value in fields:
        result[name] = value.isoformat() if isinstance(value, datetime) else value
    return result


def my_asdict(obj):
    return asdict(obj, dict_factory=_dict_factory_handle_date)


class _Database:
    _host = config['DATABASE_HOST']
    _port = 27017

    def __init__(self):
        self._mongo_client = MongoClient(self._host, self._port)
        self._itc_db = self._mongo_client.internet_threshold_checker
        self._readings = self._itc_db.readings

    def save_reading(self, reading: Reading):
        self._readings.insert_one(my_asdict(reading))

    def get_weekly_readings(self) -> ReadingGroup:
        date = datetime.now()
        normalised_weekday = (date.weekday() + 1) % 7
        week_start: datetime = (date - timedelta(days=normalised_weekday)) \
            .replace(hour=0, minute=0, second=0, microsecond=0)
        week_end: datetime = week_start + timedelta(days=7) - timedelta(microseconds=1)
        week_start_iso = week_start.isoformat()
        week_end_iso = week_end.isoformat()
        readings = list(self._readings
                        .find({'date': {'$gt': week_start_iso, '$lt': week_end_iso}})
                        .sort('date'))
        readings = list(map(Reading.from_dict, readings))
        return ReadingGroup(readings, week_start, week_end)

    def get_last_reading(self) -> Reading or None:
        reading_group = self.get_weekly_readings()
        readings = reading_group.readings
        if len(readings) > 0:
            return readings[-1]
        return None


database = _Database()
