"""
AI Skin Health Monitor — Backend & Insights (Member 4).
FastAPI app: auth, health-insight, history, session, analyse gateway; health check.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, health_insight, history, session_delete, analyse

app = FastAPI(
    title="AI Skin Health Monitor — Backend & Insights",
    description="REST API gateway, health scoring, recommendations, persistence",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check for Docker / load balancer (Section 10.3)
@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}

# API under /api so frontend can POST /api/analyse (Section 4.2 Step 4)
app.include_router(auth.router, prefix="/api")
app.include_router(health_insight.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(session_delete.router, prefix="/api")
app.include_router(analyse.router, prefix="/api")

# Also expose at root for direct service-to-service (e.g. health-insight)
app.include_router(auth.router)
app.include_router(health_insight.router)
app.include_router(history.router)
app.include_router(session_delete.router)
app.include_router(analyse.router)
