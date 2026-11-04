from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    tasks = crud.get_tasks(db)
    counts = crud.get_task_counts(db)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"tasks": tasks, "counts": counts},
    )
