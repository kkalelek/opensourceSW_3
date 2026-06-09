# AGENTS.md

## Project overview
- This project is a FastAPI backend for a classroom availability website.
- For now, support only the IT융합대학 building.
- The base classroom availability calculation uses the provided CSV timetable file.
- MySQL is used only for administrator accounts and administrator room status overrides.

## Tech stack
- Use Python and FastAPI only.
- Do not introduce other backend frameworks.
- Keep the base timetable lookup CSV-based.
- Do not migrate the timetable calculation to MySQL unless explicitly requested.
- MySQL may be used for:
  - administrator accounts
  - administrator temporary room status overrides

## Data source
- Use `backend/app/data/timetable_it.csv` as the source for timetable-based classroom schedules.
- Read the actual CSV columns first and adapt parsers to the real file format.
- Do not assume column names before inspecting the CSV.
- Normalize weekday and time values before applying availability logic.
- Store and compare `room` override values using the same original room string returned by `available-now`.

## Features
- Show classroom availability for the selected building at the current time.
- Show available classrooms for a user-provided time range.
- Support only the IT융합대학 building for now.
- Support administrator login.
- Support administrator temporary room status override storage in MySQL.

## Availability rules
- Use only `white`, `yellow`, and `green`.
- Never add or return a `red` status.
- If a class is currently in progress in a room, mark it as `white`.
- If no class is currently in progress and the next class starts in less than 1 hour, mark it as `yellow`.
- If no class is currently in progress and the next class starts in 1 hour or more, mark it as `green`.
- If there are no more classes for that room today, mark it as `green`.
- Administrator override `occupied` must return final `status="white"`.
- Administrator override `available` must return final `status="green"`.
- Preserve the CSV-based status in `base_status` when an override is applied.

## Time-range query rules
- A room is available for a requested time range only if no CSV timetable class overlaps with that entire time range.
- Treat overlapping time ranges carefully and use proper time comparisons.
- Reject invalid ranges where start time is equal to or later than end time.
- Do not apply administrator overrides to `available-range` unless explicitly requested.

## API expectations
- Implement backend APIs only.
- Keep existing API paths stable.
- Provide one API for current-time availability.
- Provide one API for time-range availability.
- Provide administrator-only APIs for login and room status overrides.
- Validate request inputs carefully.
- Return clear error messages for invalid building names, invalid rooms, invalid time ranges, and invalid override requests.
- Keep response formats simple and consistent.

## Out of scope
- Do not implement general user signup or general user login.
- Do not implement frontend UI.
- Do not implement WebSocket or other realtime transport unless explicitly requested.
- Do not implement exam, event, construction, or other exception handling.
- Do not implement classroom capacity or equipment info.
- Do not implement support for other buildings yet.

## Code organization
- Keep the code simple and readable.
- Separate routers, services, schemas, repositories, dependencies, and utility logic.
- Avoid unnecessary abstraction.
- Add comments only where they improve understanding.
- Prefer small, focused functions over large complex functions.

## Expected project structure
- Organize the project under a backend directory.
- Suggested structure:
  - backend/app/main.py
  - backend/app/routers/
  - backend/app/services/
  - backend/app/schemas/
  - backend/app/repositories/
  - backend/app/dependencies/
  - backend/app/utils/
  - backend/app/data/
  - backend/scripts/
  - backend/tests/
  - database/

## Implementation notes
- Use Python datetime/time utilities for time comparison instead of plain string comparison.
- Handle weekday normalization consistently.
- Treat administrator `expires_at` values as Asia/Seoul time.
- If a request includes timezone information, normalize it to Asia/Seoul before storing.
- If a request omits timezone information, interpret it as Asia/Seoul local time.
- Keep building handling simple; only IT융합대학 needs to work in this version.
- Do not add features beyond the requested scope without explicit instruction.
- Do not hardcode secrets, database passwords, or token secrets in source files.

## Testing
- Add tests for the core room-availability logic.
- Test current class detection.
- Test green / yellow / white classification.
- Test time-range overlap logic.
- Test invalid input handling.
- Test administrator login and override behavior with a fake repository or mock so real MySQL data is not polluted.
- Use pytest.

## Run commands
- Install dependencies with a standard Python workflow.
- Provide a requirements file.
- Document how to run the FastAPI server locally.
- Document how to run tests locally.

## Done when
- The FastAPI server runs locally without errors.
- The CSV file is parsed correctly.
- Current-time availability works for IT융합대학.
- Time-range availability works for IT융합대학.
- Administrator login and override APIs work without changing CSV timetable logic.
- Core tests pass.
- README explains how to install dependencies, configure environment variables, run the server, and run tests.
