from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo

from app.utils.constants import VALID_DAY_CODES, WEEKDAY_TO_CODE

SEOUL_TZ = ZoneInfo("Asia/Seoul")
PYTHON_WEEKDAY_TO_CODE = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")


def parse_hhmm(value: str) -> time:
    try:
        return time.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Time must use HH:MM format.") from exc


def format_hhmm(value: time) -> str:
    return value.strftime("%H:%M")


def normalize_weekday(raw_weekday: str) -> str:
    try:
        return WEEKDAY_TO_CODE[raw_weekday]
    except KeyError as exc:
        raise ValueError("Unsupported weekday value in CSV.") from exc


def validate_day_code(day: str) -> str:
    normalized = day.strip().upper()
    if normalized not in VALID_DAY_CODES:
        raise ValueError("day must be one of MON, TUE, WED, THU, FRI, SAT, SUN.")
    return normalized


def get_current_day_and_time() -> tuple[str, time]:
    now = datetime.now(SEOUL_TZ)
    return PYTHON_WEEKDAY_TO_CODE[now.weekday()], now.timetz().replace(tzinfo=None)


def is_time_in_range(target: time, start: time, end: time) -> bool:
    return start <= target < end


def minutes_until(start: time, end: time) -> int:
    start_minutes = (start.hour * 60) + start.minute
    end_minutes = (end.hour * 60) + end.minute
    return end_minutes - start_minutes


def has_overlap(
    requested_start: time,
    requested_end: time,
    class_start: time,
    class_end: time,
) -> bool:
    return requested_start < class_end and class_start < requested_end
