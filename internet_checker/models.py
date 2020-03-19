from dataclasses import dataclass
from datetime import datetime
from typing import List

from .config import config

_threshold = config['DISCONNECT_THRESHOLD']
_daily_threshold = config['DAILY_THRESHOLD']


@dataclass
class DetailedStatus:
    percentage: float
    days_to_renew: int
    actual_remaining_gb: float
    mean_daily_left_gb: float
    actual_daily_left_gb: float


@dataclass
class Reading:
    total_gb: float
    remaining_gb: float
    date = datetime.now()

    @staticmethod
    def from_dict(reading_dict):
        total_gb = reading_dict['total_gb']
        remaining_gb = reading_dict['remaining_gb']
        return Reading(total_gb, remaining_gb)

    def get_detailed_status(self) -> DetailedStatus:
        percentage = (self.remaining_gb / self.total_gb) * 100
        days_to_renew = 7 - ((self.date.weekday() + 1) % 7)
        actual_remaining_gb = self.remaining_gb - (self.total_gb / 100) * _threshold
        mean_daily_left_gb = (actual_remaining_gb / (days_to_renew - 1)
                              ) if days_to_renew > 1 else actual_remaining_gb
        actual_daily_left_gb = actual_remaining_gb - (_daily_threshold * (days_to_renew - 1))
        return DetailedStatus(percentage, days_to_renew, actual_remaining_gb, mean_daily_left_gb, actual_daily_left_gb)


@dataclass
class Status:
    reading: Reading
    connected: bool
    traffic_exceeded: bool


@dataclass
class StatusResponse:
    status: Status
    details: DetailedStatus


@dataclass
class ReadingGroup:
    readings: List[Reading]
    start_date_iso: str
    end_date_iso: str
