from app.utils.constants import SUPPORTED_BUILDING
from app.utils.parsers import parse_schedule_chunk, split_schedule_text


def test_split_schedule_text_returns_each_schedule_item() -> None:
    schedule_text = (
        "\uD65410:00~12:00(IT\uC735\uD569\uB300\uD559-\uACF5\uC6A9PC\uC2E41(3208)), "
        "\uBAA910:00~12:00(IT\uC735\uD569\uB300\uD559-\uACF5\uC6A9PC\uC2E41(3208))"
    )

    parts = split_schedule_text(schedule_text)

    assert len(parts) == 2


def test_parse_schedule_chunk_preserves_original_location() -> None:
    chunk = parse_schedule_chunk(
        "\uC6D416:00~18:00(IT\uC735\uD569\uB300\uD5593224 \uAC15\uC758\uC2E4)"
    )

    assert chunk is not None
    assert chunk.location == "IT\uC735\uD569\uB300\uD5593224 \uAC15\uC758\uC2E4"
    assert chunk.building == SUPPORTED_BUILDING
