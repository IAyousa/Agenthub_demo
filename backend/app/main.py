from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import agents, conversations, messages, artifacts

app = FastAPI(
    title="Agenthub API",
    description="Multi-Agent Collaboration Platform API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["conversations"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])
app.include_router(artifacts.router, prefix="/api/v1/artifacts", tags=["artifacts"])

@app.get("/")
async def root():
    return {"message": "Welcome to Agenthub API", "docs": "/docs"}
