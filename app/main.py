from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .database import Base, engine
from .routers import auth_routes, projects_routes, tasks_routes

# Auto-create tables on startup (for hackathon / demo). In real prod, prefer Alembic.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API",
    version="1.0.0",
    description="A clean, secure REST API for projects & tasks with JWT auth.",
    contact={"name": "Your Name", "email": "you@example.com"},
    license_info={"name": "MIT"},
)

# Error normalization (example of centralized handling)
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})

app.include_router(auth_routes.router)
app.include_router(projects_routes.router)
app.include_router(tasks_routes.router)
