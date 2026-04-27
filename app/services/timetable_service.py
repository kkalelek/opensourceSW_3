from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from datetime import time

from backend.app.schemas.availability import (
    AvailableNowResponse,
    AvailableRangeResponse,
    AvailableRangeRoom,
    ParsedScheduleSummary,
    RoomAvailability,
    ScheduleEntry,
)
from app.utils.constants import SUPPORTED_BUILDING
from app.utils.parsers import parse_schedule_chunks
from app.utils.time_utils import (
    format_hhmm,
    get_current_day_and_time,
    has_overlap,
    is_time_in_range,
    normalize_weekday,
    parse_hhmm,
    validate_day_code,
    minutes_until,
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE_PATH = BASE_DIR / "data" / "timetable_it.csv"
MAJOR_COLUMN = "\uC804\uACF5"
COURSE_NAME_COLUMN = "\uACFC\uBAA9\uBA85"
TIME_COLUMN = "\uC2DC\uAC04"


@dataclass(frozen=True)
class ParsedClassTime:
    major: str
    course_name: str
    weekday: str
    weekday_code: str
    start_time: time
    end_time: time
    location: str
    building: str


class TimetableService:
    def __init__(self, csv_path: Path) -> None:
        self.csv_path = csv_path
        self._entries = self._load_entries()

    def _load_entries(self) -> list[ParsedClassTime]:
        rows = self._read_csv_rows()
        entries = self._parse_rows(rows)
        return sorted(
            entries,
            key=lambda entry: (entry.location, entry.weekday_code, entry.start_time, entry.end_time),
        )

    def _read_csv_rows(self) -> list[dict[str, str]]:
        with self.csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            return [dict(row) for row in reader]

    def _parse_rows(self, rows: list[dict[str, str]]) -> list[ParsedClassTime]:
        entries: list[ParsedClassTime] = []

        for row in rows:
            major = (row.get(MAJOR_COLUMN) or "").strip()
            course_name = (row.get(COURSE_NAME_COLUMN) or "").strip()
            raw_schedule = (row.get(TIME_COLUMN) or "").strip()

            for chunk in parse_schedule_chunks(raw_schedule):
                if SUPPORTED_BUILDING not in chunk.location:
                    continue

                entries.append(
                    ParsedClassTime(
                        major=major,
                        course_name=course_name,
                        weekday=chunk.weekday,
                        weekday_code=normalize_weekday(chunk.weekday),
                        start_time=parse_hhmm(chunk.start_time),
                        end_time=parse_hhmm(chunk.end_time),
                        location=chunk.location,
                        building=chunk.building,
                    )
                )

        return entries

    def list_entries(self) -> list[ParsedClassTime]:
        return list(self._entries)

    def list_room_names(self) -> list[str]:
        return sorted({entry.location for entry in self._entries})

    def _validate_building(self, building: str) -> None:
        if building != SUPPORTED_BUILDING:
            raise ValueError(f"Only {SUPPORTED_BUILDING} is supported.")

    def _get_day_entries_for_room(self, room: str, day_code: str) -> list[ParsedClassTime]:
        room_entries = [
            entry
            for entry in self._entries
            if entry.location == room and entry.weekday_code == day_code
        ]
        return sorted(room_entries, key=lambda entry: entry.start_time)

    def get_summary(self) -> ParsedScheduleSummary:
        sample_entries = [
            ScheduleEntry(
                major=entry.major,
                course_name=entry.course_name,
                weekday=entry.weekday,
                weekday_code=entry.weekday_code,
                start_time=format_hhmm(entry.start_time),
                end_time=format_hhmm(entry.end_time),
                location=entry.location,
                building=entry.building,
            )
            for entry in self._entries[:10]
        ]

        return ParsedScheduleSummary(
            building=SUPPORTED_BUILDING,
            total_entries=len(self._entries),
            total_rooms=len(self.list_room_names()),
            sample_entries=sample_entries,
        )

    def get_available_now(self, building: str) -> AvailableNowResponse:
        self._validate_building(building)
        day_code, current_time = get_current_day_and_time()
        rooms = [
            self._build_now_room_availability(room, day_code, current_time)
            for room in self.list_room_names()
        ]
        return AvailableNowResponse(
            building=SUPPORTED_BUILDING,
            day=day_code,
            query_time=format_hhmm(current_time),
            rooms=rooms,
        )

    def _build_now_room_availability(
        self,
        room: str,
        day_code: str,
        current_time: time,
    ) -> RoomAvailability:
        entries = self._get_day_entries_for_room(room, day_code)

        current_entry = self._find_current_entry(entries, current_time)
        if current_entry is not None:
            return RoomAvailability(
                room=room,
                status="white",
                current_course_name=current_entry.course_name,
                current_class_end=format_hhmm(current_entry.end_time),
                next_course_name=None,
                next_class_start=None,
            )

        next_entry = self._find_next_entry(entries, current_time)
        if next_entry is None:
            return RoomAvailability(room=room, status="green")

        gap_minutes = minutes_until(current_time, next_entry.start_time)
        status = "yellow" if gap_minutes < 60 else "green"

        return RoomAvailability(
            room=room,
            status=status,
            next_course_name=next_entry.course_name,
            next_class_start=format_hhmm(next_entry.start_time),
        )

    def _find_current_entry(
        self,
        entries: list[ParsedClassTime],
        current_time: time,
    ) -> ParsedClassTime | None:
        for entry in entries:
            if is_time_in_range(current_time, entry.start_time, entry.end_time):
                return entry
        return None

    def _find_next_entry(
        self,
        entries: list[ParsedClassTime],
        current_time: time,
    ) -> ParsedClassTime | None:
        for entry in entries:
            if entry.start_time > current_time:
                return entry
        return None

    def get_available_range(
        self,
        building: str,
        day: str,
        start: str,
        end: str,
    ) -> AvailableRangeResponse:
        self._validate_building(building)
        day_code = validate_day_code(day)
        start_time = parse_hhmm(start)
        end_time = parse_hhmm(end)

        if start_time >= end_time:
            raise ValueError("start must be earlier than end.")

        available_rooms = []
        for room in self.list_room_names():
            day_entries = self._get_day_entries_for_room(room, day_code)
            if self._is_room_available_for_range(day_entries, start_time, end_time):
                available_rooms.append(AvailableRangeRoom(room=room))

        return AvailableRangeResponse(
            building=SUPPORTED_BUILDING,
            day=day_code,
            start=format_hhmm(start_time),
            end=format_hhmm(end_time),
            rooms=available_rooms,
        )

    def _is_room_available_for_range(
        self,
        entries: list[ParsedClassTime],
        start_time: time,
        end_time: time,
    ) -> bool:
        for entry in entries:
            if has_overlap(start_time, end_time, entry.start_time, entry.end_time):
                return False
        return True


@lru_cache
def get_timetable_service() -> TimetableService:
    return TimetableService(csv_path=DATA_FILE_PATH)
