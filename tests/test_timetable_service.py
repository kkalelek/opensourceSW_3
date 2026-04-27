from datetime import time

import pytest

from app.services.timetable_service import ParsedClassTime, TimetableService


def build_service(entries: list[ParsedClassTime]) -> TimetableService:
    service = TimetableService.__new__(TimetableService)
    service.csv_path = None
    service._entries = sorted(
        entries,
        key=lambda entry: (entry.location, entry.weekday_code, entry.start_time, entry.end_time),
    )
    return service


def build_entry(
    *,
    course_name: str,
    weekday: str = "\uC6D4",
    weekday_code: str = "MON",
    start_hour: int,
    end_hour: int,
    location: str = "IT\uC735\uD569\uB300\uD559-TEST(1001)",
) -> ParsedClassTime:
    return ParsedClassTime(
        major="Test Major",
        course_name=course_name,
        weekday=weekday,
        weekday_code=weekday_code,
        start_time=time(start_hour, 0),
        end_time=time(end_hour, 0),
        location=location,
        building="IT\uC735\uD569\uB300\uD559",
    )


def test_available_now_returns_white_when_class_is_in_progress() -> None:
    service = build_service(
        [build_entry(course_name="Algorithms", start_hour=9, end_hour=11)]
    )

    result = service._build_now_room_availability(
        room="IT\uC735\uD569\uB300\uD559-TEST(1001)",
        day_code="MON",
        current_time=time(10, 0),
    )

    assert result.status == "white"
    assert result.current_course_name == "Algorithms"
    assert result.current_class_end == "11:00"


def test_available_now_returns_yellow_when_next_class_is_within_one_hour() -> None:
    service = build_service(
        [build_entry(course_name="Networks", start_hour=10, end_hour=12)]
    )

    result = service._build_now_room_availability(
        room="IT\uC735\uD569\uB300\uD559-TEST(1001)",
        day_code="MON",
        current_time=time(9, 30),
    )

    assert result.status == "yellow"
    assert result.next_course_name == "Networks"
    assert result.next_class_start == "10:00"


def test_available_now_returns_green_when_next_class_is_one_hour_or_more_away() -> None:
    service = build_service(
        [build_entry(course_name="Databases", start_hour=11, end_hour=12)]
    )

    result = service._build_now_room_availability(
        room="IT\uC735\uD569\uB300\uD559-TEST(1001)",
        day_code="MON",
        current_time=time(9, 30),
    )

    assert result.status == "green"
    assert result.next_class_start == "11:00"


def test_available_now_returns_green_when_next_class_is_exactly_one_hour_away() -> None:
    service = build_service(
        [build_entry(course_name="AI", start_hour=11, end_hour=12)]
    )

    result = service._build_now_room_availability(
        room="IT\uC735\uD569\uB300\uD559-TEST(1001)",
        day_code="MON",
        current_time=time(10, 0),
    )

    assert result.status == "green"
    assert result.next_class_start == "11:00"


def test_available_now_returns_green_when_no_more_classes_today() -> None:
    service = build_service(
        [build_entry(course_name="OS", start_hour=9, end_hour=10)]
    )

    result = service._build_now_room_availability(
        room="IT\uC735\uD569\uB300\uD559-TEST(1001)",
        day_code="MON",
        current_time=time(15, 0),
    )

    assert result.status == "green"
    assert result.next_class_start is None


def test_available_range_returns_only_rooms_without_overlap() -> None:
    service = build_service(
        [
            build_entry(
                course_name="Compilers",
                start_hour=13,
                end_hour=15,
                location="IT\uC735\uD569\uB300\uD559-ROOM-A(1001)",
            ),
            build_entry(
                course_name="Math",
                start_hour=16,
                end_hour=17,
                location="IT\uC735\uD569\uB300\uD559-ROOM-B(1002)",
            ),
        ]
    )

    result = service.get_available_range(
        building="IT\uC735\uD569\uB300\uD559",
        day="MON",
        start="14:00",
        end="16:00",
    )

    assert [room.room for room in result.rooms] == ["IT\uC735\uD569\uB300\uD559-ROOM-B(1002)"]


def test_available_range_rejects_invalid_building() -> None:
    service = build_service([])

    with pytest.raises(ValueError, match="Only"):
        service.get_available_range(
            building="MainHall",
            day="MON",
            start="14:00",
            end="16:00",
        )


def test_available_range_rejects_start_greater_than_or_equal_to_end() -> None:
    service = build_service([])

    with pytest.raises(ValueError, match="start must be earlier than end"):
        service.get_available_range(
            building="IT\uC735\uD569\uB300\uD559",
            day="MON",
            start="16:00",
            end="16:00",
        )


def test_available_range_rejects_invalid_time_format() -> None:
    service = build_service([])

    with pytest.raises(ValueError, match="HH:MM"):
        service.get_available_range(
            building="IT\uC735\uD569\uB300\uD559",
            day="MON",
            start="2pm",
            end="16:00",
        )


def test_available_range_rejects_invalid_day_code() -> None:
    service = build_service([])

    with pytest.raises(ValueError, match="day must be one of"):
        service.get_available_range(
            building="IT\uC735\uD569\uB300\uD559",
            day="MONDAY",
            start="14:00",
            end="16:00",
        )
