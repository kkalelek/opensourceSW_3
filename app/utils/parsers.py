from __future__ import annotations

import re
from dataclasses import dataclass

from app.utils.constants import SUPPORTED_BUILDING

SCHEDULE_PATTERN = re.compile(
    r"^\s*([\uC6D4\uD654\uC218\uBAA9\uAE08\uD1A0\uC77C])\s*(\d{1,2}:\d{2})~(\d{1,2}:\d{2})\((.+)\)\s*$"
)


@dataclass(frozen=True)
class ScheduleChunk:
    weekday: str
    start_time: str
    end_time: str
    location: str
    building: str


def split_schedule_text(schedule_text: str) -> list[str]:
    if not schedule_text.strip():
        return []
    return [part.strip() for part in schedule_text.split(",") if part.strip()]


def extract_building(location: str) -> str:
    normalized = location.strip()
    if normalized.startswith(f"{SUPPORTED_BUILDING}-"):
        return SUPPORTED_BUILDING
    if normalized.startswith(SUPPORTED_BUILDING):
        return SUPPORTED_BUILDING
    if "-" in normalized:
        return normalized.split("-", 1)[0].strip()
    return normalized


def parse_schedule_chunk(chunk_text: str) -> ScheduleChunk | None:
    match = SCHEDULE_PATTERN.match(chunk_text)
    if not match:
        return None

    weekday, start_time, end_time, location = match.groups()

    return ScheduleChunk(
        weekday=weekday,
        start_time=start_time,
        end_time=end_time,
        location=location.strip(),
        building=extract_building(location),
    )


def parse_schedule_chunks(schedule_text: str) -> list[ScheduleChunk]:
    chunks: list[ScheduleChunk] = []

    for chunk_text in split_schedule_text(schedule_text):
        parsed = parse_schedule_chunk(chunk_text)
        if parsed is not None:
            chunks.append(parsed)

    return chunks
