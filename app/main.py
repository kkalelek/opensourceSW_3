from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.availability import router as availability_router


app = FastAPI(
    
    title="Classroom Availability API",
    description="FastAPI backend for IT building classroom availability.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(availability_router)


@app.get("/", tags=["health"])
def read_root() -> dict[str, str]:
    return {"message": "Classroom Availability API is running."}
