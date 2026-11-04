from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Task
from app.schemas import TaskCreate, TaskUpdate


def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)


def get_tasks(db: Session) -> list[Task]:
    statement = select(Task).order_by(Task.created_at.desc(), Task.id.desc())
    return list(db.scalars(statement))


def create_task(db: Session, payload: TaskCreate) -> Task:
    task = Task(title=payload.title, description=payload.description)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: Task, payload: TaskUpdate) -> Task:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


def get_task_counts(db: Session) -> dict[str, int]:
    total = db.scalar(select(func.count()).select_from(Task)) or 0
    completed = db.scalar(
        select(func.count()).select_from(Task).where(Task.is_completed.is_(True))
    ) or 0
    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
    }
