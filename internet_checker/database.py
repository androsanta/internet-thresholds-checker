from datetime import datetime, timedelta

from pymongo import MongoClient

from .config import config

_threshold = config['DISCONNECT_THRESHOLD']
_daily_threshold = config['DAILY_THRESHOLD']


class Reading:
    def __init__(self, remaining_gb: float = None, total_gb: float = None):
        if remaining_gb is None or total_gb is None:
            return

        self.remaining_gb = remaining_gb
        self.total_gb = total_gb
        self.percentage = (remaining_gb / total_gb) * 100
        self.date = datetime.now()
        self.days_to_renew = 7 - ((self.date.weekday() + 1) % 7)
        self.actual_remaining_gb = remaining_gb - (total_gb / 100) * _threshold
        self.mean_daily_left_gb = (self.actual_remaining_gb / (self.days_to_renew - 1)
                                   ) if self.days_to_renew > 1 else self.actual_remaining_gb
        self.actual_daily_left_gb = self.actual_remaining_gb - (_daily_threshold * (self.days_to_renew - 1))

    def to_dict(self) -> dict:
        return {
            'remainingGb': self.remaining_gb,
            'totalGb': self.total_gb,
            'percentage': self.percentage,
            'date': str(self.date.isoformat()),
            'daysToRenew': self.days_to_renew,
            'actualRemainingGb': self.actual_remaining_gb,
            'meanDailyLeftGb': self.mean_daily_left_gb,
            'actualDailyLeftGb': self.actual_daily_left_gb
        }

    @staticmethod
    def from_dict(reading_dict):
        reading = Reading()
        reading.remaining_gb = reading_dict['remainingGb']
        reading.total_gb = reading_dict['totalGb']
        reading.percentage = reading_dict['percentage']
        reading.date = datetime.fromisoformat(reading_dict['date'])
        reading.days_to_renew = reading_dict['daysToRenew']
        reading.actual_remaining_gb = reading_dict['actualRemainingGb']
        reading.mean_daily_left_gb = reading_dict['meanDailyLeftGb']
        reading.actual_daily_left_gb = reading_dict['actualDailyLeftGb']
        return reading


class _Database:
    _host = config['DATABASE_HOST']
    _port = 27017

    def __init__(self):
        self._mongo_client = MongoClient(self._host, self._port)
        self._itc_db = self._mongo_client.internet_threshold_checker
        self._readings = self._itc_db.readings

    def save_reading(self, reading: Reading):
        self._readings.insert_one(reading.to_dict())

    def get_weekly_readings(self, date: datetime):
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
        return {
            'readings': readings,
            'startDate': week_start.isoformat(),
            'endDate': week_end.isoformat()
        }

    def get_last_reading(self):
        result = self.get_weekly_readings(datetime.now())
        readings = result['readings']
        if len(readings) > 0:
            return readings[-1]
        return None


database = _Database()
