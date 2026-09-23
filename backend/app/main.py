from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from app.routers import assistant, pr, quotations, po, receiving, budget, auth, suppliers
from app.services.db import connect_db, disconnect_db, check_db_health

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect to database
    await connect_db()
    yield
    # Shutdown: disconnect from database
    await disconnect_db()

app = FastAPI(
    title="AI Procurement & Purchase Approval System API",
    description="FastAPI Backend for MIS3032_1 Group 01 Project",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(assistant.router)
app.include_router(pr.router)
app.include_router(suppliers.router)
app.include_router(quotations.router)
app.include_router(quotations.pr_quotations_router)
app.include_router(po.router)
app.include_router(receiving.router)
app.include_router(budget.router)

@app.get("/")
def root():
    return {
        "system": "AI Procurement System",
        "version": "1.0.0",
        "status": "ONLINE",
        "docs": "/docs"
    }

@app.get("/api/health")
async def healthcheck(response: Response):
    db_health = await check_db_health()
    if not db_health.get("healthy"):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "unhealthy",
            "database": "PostgreSQL Disconnected",
            "error": db_health.get("error"),
            "ai_service": "Active (Mock Fast Fallback)"
        }
    return {
        "status": "ok",
        "database": "PostgreSQL Connected (Prisma)",
        "db_details": db_health,
        "ai_service": "Active (Mock Fast Fallback)"
    }
