from datetime import datetime, timedelta

from pymongo import MongoClient

from app import config


class Reading:
    def __init__(self, remaining_gb: float = None, total_gb: float = None):
        if remaining_gb is None or total_gb is None:
            return

        self.remaining_gb = remaining_gb
        self.total_gb = total_gb
        self.date = datetime.now()
        self.days_to_renew = 7 - ((self.date.weekday() + 1) % 7)
        self.daily_traffic_left_gb = (remaining_gb / self.days_to_renew)
        self.percentage = (remaining_gb / total_gb) * 100

    def to_dict(self) -> dict:
        return {
            'remainingGb': self.remaining_gb,
            'totalGb': self.total_gb,
            'date': str(self.date.isoformat()),
            'daysToRenew': self.days_to_renew,
            'dailyTrafficLeftGb': self.daily_traffic_left_gb,
            'percentage': self.percentage
        }

    @staticmethod
    def from_dict(reading_dict):
        reading = Reading()
        reading.remaining_gb = reading_dict['remainingGb']
        reading.total_gb = reading_dict['totalGb']
        reading.date = datetime.fromisoformat(reading_dict['date'])
        reading.days_to_renew = reading_dict['daysToRenew']
        reading.daily_traffic_left_gb = reading_dict['dailyTrafficLeftGb']
        reading.percentage = reading_dict['percentage']
        return reading


class _Database:
    _host = config['db_host']
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


database = _Database()
