from fastapi import FastAPI

from backend.app.routers.availability import router as availability_router


app = FastAPI(
    title="Classroom Availability API",
    description="FastAPI backend for IT building classroom availability.",
    version="0.1.0",
)

app.include_router(availability_router)


@app.get("/", tags=["health"])
def read_root() -> dict[str, str]:
    return {"message": "Classroom Availability API is running."}
