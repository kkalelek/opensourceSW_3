from typing import Literal

from pydantic import BaseModel, Field


AvailabilityStatus = Literal["white", "yellow", "green"]


class ScheduleEntry(BaseModel):
    major: str = Field(..., description="Major name")
    course_name: str = Field(..., description="Course name")
    weekday: str = Field(..., description="Original weekday value")
    weekday_code: str = Field(..., description="Normalized weekday code")
    start_time: str = Field(..., description="Class start time")
    end_time: str = Field(..., description="Class end time")
    location: str = Field(..., description="Location string preserved from CSV")
    building: str = Field(..., description="Extracted building name")


class ParsedScheduleSummary(BaseModel):
    building: str = Field(..., description="Supported building name")
    total_entries: int = Field(..., description="Total parsed class entries")
    total_rooms: int = Field(..., description="Unique IT building locations")
    sample_entries: list[ScheduleEntry] = Field(
        default_factory=list,
        description="Sample parsed entries",
    )


class RoomAvailability(BaseModel):
    room: str = Field(..., description="Original location text from CSV")
    status: AvailabilityStatus = Field(..., description="Availability status color")
    current_course_name: str | None = Field(
        default=None,
        description="Current course name if a class is in progress",
    )
    current_class_end: str | None = Field(
        default=None,
        description="Current class end time if a class is in progress",
    )
    next_course_name: str | None = Field(
        default=None,
        description="Next course name if one exists later today",
    )
    next_class_start: str | None = Field(
        default=None,
        description="Next class start time if one exists later today",
    )


class AvailableNowResponse(BaseModel):
    building: str = Field(..., description="Supported building name")
    day: str = Field(..., description="Normalized weekday code")
    query_time: str = Field(..., description="Current time used for lookup")
    rooms: list[RoomAvailability] = Field(
        default_factory=list,
        description="Current room availability results",
    )


class AvailableRangeRoom(BaseModel):
    room: str = Field(..., description="Original location text from CSV")


class AvailableRangeResponse(BaseModel):
    building: str = Field(..., description="Supported building name")
    day: str = Field(..., description="Normalized weekday code")
    start: str = Field(..., description="Requested start time")
    end: str = Field(..., description="Requested end time")
    rooms: list[AvailableRangeRoom] = Field(
        default_factory=list,
        description="Rooms that do not overlap the requested time range",
    )
