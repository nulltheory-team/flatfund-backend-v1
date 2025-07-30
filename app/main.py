from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from . import models, database
from .routers import apartment

# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="FlatFund API",
    description="Apartment Management System API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(apartment.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to the FlatFund API",
        "admin_ui": "/static/admin.html",
        "docs": "/docs",
        "redoc": "/redoc"
    }