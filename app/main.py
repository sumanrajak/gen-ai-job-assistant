from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from app.api.routes import analyze_job, saved_jobs
import uvicorn

app = FastAPI(title="Gen AI Job Assistant")

# Mount static and template directories
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(analyze_job.router)
app.include_router(saved_jobs.router)
from fastapi.responses import FileResponse

# Root route (optional)from fastapi.responses import FileResponse

@app.get("/")
async def root():
    return FileResponse("app/static/index.html")

@app.get("/saved-jobs")
async def saved_jobs_page():
    return FileResponse("app/static/saved_jobs.html")

@app.get("/country-list")
async def saved_jobs_page():
    return FileResponse("app/static/countries.html")

# Run via: uvicorn app.main:app --reload
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
