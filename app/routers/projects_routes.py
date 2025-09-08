from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..deps import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=list[schemas.ProjectOut], summary="List my projects")
def list_projects(
    params: schemas.PageParams = Depends(),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    q = db.query(models.Project).filter(models.Project.owner_id == user.id)
    items = q.offset(params.offset).limit(params.limit).all()
    return items

@router.post("", response_model=schemas.ProjectOut, status_code=201, summary="Create project")
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    exists = db.query(models.Project).filter(
        models.Project.owner_id == user.id, models.Project.name == payload.name
    ).first()
    if exists:
        raise HTTPException(status_code=409, detail="Project with this name already exists")
    project = models.Project(name=payload.name, description=payload.description, owner_id=user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def _get_owned_project(db: Session, user_id: int, project_id: int) -> models.Project:
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/{project_id}", response_model=schemas.ProjectOut, summary="Get project")
def get_project(project_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return _get_owned_project(db, user.id, project_id)

@router.put("/{project_id}", response_model=schemas.ProjectOut, summary="Update project")
def update_project(project_id: int, payload: schemas.ProjectUpdate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    project = _get_owned_project(db, user.id, project_id)
    if payload.name and payload.name != project.name:
        dup = db.query(models.Project).filter(models.Project.owner_id == user.id, models.Project.name == payload.name).first()
        if dup:
            raise HTTPException(status_code=409, detail="Project with this name already exists")
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=204, summary="Delete project (cascades tasks)")
def delete_project(project_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    project = _get_owned_project(db, user.id, project_id)
    db.delete(project)
    db.commit()
    return
