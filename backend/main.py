from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Rihla-AI Backend starting...")
    yield
    # Shutdown
    print("Rihla-AI Backend shutting down...")


app = FastAPI(
    title="Rihla-AI Backend",
    description="Agentic AI Travel Agency Backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "rihla-backend"}
