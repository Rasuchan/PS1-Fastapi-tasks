from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..deps import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("", response_model=list[schemas.TaskOut], summary="List tasks (optionally filter by project)")
def list_tasks(
    params: schemas.PageParams = Depends(),
    project_id: int | None = None,
    done: bool | None = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    q = db.query(models.Task).filter(models.Task.owner_id == user.id)
    if project_id is not None:
        q = q.filter(models.Task.project_id == project_id)
    if done is not None:
        q = q.filter(models.Task.done == done)
    return q.offset(params.offset).limit(params.limit).all()

@router.post("", response_model=schemas.TaskOut, status_code=201, summary="Create task")
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # Ensure project belongs to user
    proj = db.query(models.Project).filter(models.Project.id == payload.project_id, models.Project.owner_id == user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    task = models.Task(
        title=payload.title,
        description=payload.description,
        done=payload.done or False,
        project_id=payload.project_id,
        owner_id=user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def _get_owned_task(db: Session, user_id: int, task_id: int) -> models.Task:
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/{task_id}", response_model=schemas.TaskOut, summary="Get task")
def get_task(task_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return _get_owned_task(db, user.id, task_id)

@router.put("/{task_id}", response_model=schemas.TaskOut, summary="Update task")
def update_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    task = _get_owned_task(db, user.id, task_id)
    if payload.project_id is not None and payload.project_id != task.project_id:
        proj = db.query(models.Project).filter(models.Project.id == payload.project_id, models.Project.owner_id == user.id).first()
        if not proj:
            raise HTTPException(status_code=404, detail="Target project not found")
        task.project_id = payload.project_id
    if payload.title is not None:
        t = payload.title.strip()
        if not t:
            raise HTTPException(status_code=422, detail="Title cannot be empty")
        task.title = t
    if payload.description is not None:
        task.description = payload.description
    if payload.done is not None:
        task.done = payload.done
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=204, summary="Delete task")
def delete_task(task_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    task = _get_owned_task(db, user.id, task_id)
    db.delete(task)
    db.commit()
    return
