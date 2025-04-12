# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import router as auth_router
from app.db import models, database
from app.routers.posts import router as posts_router
from app.routers.reports import router as report_router
from app.db.database import create_db
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title="Cyberbullying Detection System")

# Initialize database
create_db()

models.Base.metadata.create_all(bind=database.engine)   # Create tables in the database
app.add_middleware(
    SessionMiddleware,
    secret_key="your-super-secret-key"
)
# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Include routers for API
app.include_router(auth_router, prefix="/api/auth")
app.include_router(posts_router, prefix="/api/post")
app.include_router(report_router, prefix="/api/report")

# HTML frontend routes
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/auth/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.get("/auth/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@app.get("/posts", response_class=HTMLResponse)
def post_list_page(request: Request):
    return templates.TemplateResponse("posts/list.html", {"request": request})

@app.get("/posts/create", response_class=HTMLResponse)
def create_post_page(request: Request):
    return templates.TemplateResponse("posts/create.html", {"request": request})

@app.get("/reports", response_class=HTMLResponse)
def reports_list_page(request: Request):
    return templates.TemplateResponse("reports/list.html", {"request": request})

@app.get("/reports/{report_id}", response_class=HTMLResponse)
def report_detail_page(request: Request, report_id: int):
    return templates.TemplateResponse("reports/detail.html", {"request": request, "report_id": report_id})
