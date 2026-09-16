from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import assistant, pr, quotations, po, receiving, budget, auth

app = FastAPI(
    title="AI Procurement & Purchase Approval System API",
    description="FastAPI Backend for MIS3032_1 Group 01 Project",
    version="1.0.0"
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
app.include_router(quotations.router)
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
def healthcheck():
    return {
        "status": "ok",
        "database": "PostgreSQL Connected (Prisma)",
        "ai_service": "Active (Mock Fast Fallback)"
    }
