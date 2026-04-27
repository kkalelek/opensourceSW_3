# AGENTS.md

## Project overview
- This project is a backend for a classroom availability website.
- For now, support only the IT융합대학 building.
- The goal is to find available classrooms based on the provided timetable CSV file.

## Tech stack
- Use Python and FastAPI only.
- Do not introduce other backend frameworks.
- Do not add a database in the first version unless explicitly requested.

## Data source
- Use the provided CSV timetable file as the only data source.
- Read the actual CSV columns first and adapt the parser to the real file format.
- Do not assume column names before inspecting the CSV.
- Normalize weekday and time values before applying availability logic.
- If the CSV uses class periods instead of actual times, create a clear period-to-time mapping and document it.

## Features to implement
- Show available classrooms for the selected building at the current time.
- Show available classrooms for a user-provided time range.
- Support only the IT융합대학 building for now.

## Availability rules
- If a class is currently in progress in a room, mark it as `white`.
- If no class is currently in progress and the next class starts in less than 1 hour, mark it as `yellow`.
- If no class is currently in progress and the next class starts in 1 hour or more, mark it as `green`.
- If there are no more classes for that room today, mark it as `green`.

## Time-range query rules
- A room is available for a requested time range only if no class overlaps with that entire time range.
- Treat overlapping time ranges carefully and use proper time comparisons.
- Reject invalid ranges where start time is equal to or later than end time.

## API expectations
- Implement backend APIs only.
- Provide one API for current-time availability.
- Provide one API for time-range availability.
- Validate request inputs carefully.
- Return clear error messages for invalid building names or invalid time ranges.
- Keep response formats simple and consistent.

## Out of scope
- Do not implement login or authentication.
- Do not implement exam, event, construction, or other exception handling.
- Do not implement classroom capacity or equipment info.
- Do not implement support for other buildings yet.
- Do not implement frontend UI.

## Code organization
- Keep the code simple and readable.
- Separate routers, services, schemas, and utility logic.
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
  - backend/app/utils/
  - backend/app/data/
  - backend/tests/

## Implementation notes
- Use Python datetime/time utilities for time comparison instead of plain string comparison.
- Handle weekday normalization consistently.
- Keep building handling simple; only IT융합대학 needs to work in this version.
- Do not add features beyond the requested scope without explicit instruction.
- If any CSV ambiguity exists, document assumptions clearly in README or code comments.

## Testing
- Add tests for the core room-availability logic.
- Test current class detection.
- Test green / yellow / white classification.
- Test time-range overlap logic.
- Test invalid input handling.
- Use pytest.

## Run commands
- Install dependencies with a standard Python workflow.
- Provide a requirements file or pyproject file.
- Document how to run the FastAPI server locally.
- Document how to run tests locally.

## Done when
- The FastAPI server runs locally without errors.
- The CSV file is parsed correctly.
- Current-time availability works for IT융합대학.
- Time-range availability works for IT융합대학.
- Core tests pass.
- README explains how to install dependencies, run the server, and run tests.
