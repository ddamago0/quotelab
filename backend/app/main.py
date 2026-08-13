from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.health import router as health_router
from app.api.search import router as search_router
from app.api.debate import router as debate_router
from app.api.batch import router as batch_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(search_router, prefix=settings.API_PREFIX)
app.include_router(debate_router, prefix=settings.API_PREFIX)
app.include_router(batch_router, prefix=settings.API_PREFIX)





@app.get("/")
def root():
    return {"message": "Welcome to QuoteLab API", "docs": f"{settings.API_PREFIX}/docs"}
