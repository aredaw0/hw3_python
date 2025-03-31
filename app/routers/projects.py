from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=list[schemas.ProjectOut])
def get_projects(db: Session = Depends(get_db),
                 current_user: models.User = Depends(auth.get_current_user)):
    projects = db.query(models.Project).filter(models.Project.user_id == current_user.id).all()
    return projects

@router.post("/", response_model=schemas.ProjectOut)
def create_project(project_data: schemas.ProjectCreate,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(auth.get_current_user)):

    existing = db.query(models.Project).filter_by(user_id=current_user.id, name=project_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Проект с таким названием уже существует")
    new_project = models.Project(name=project_data.name, user_id=current_user.id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project
