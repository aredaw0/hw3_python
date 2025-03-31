from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, auth
from app.database import get_db
import string, random

router = APIRouter()

def generate_unique_code(db: Session, length: int = 6) -> str:
    characters = string.ascii_letters + string.digits 
    while True:
        code = ''.join(random.choice(characters) for _ in range(length))

        existing = db.query(models.Link).filter_by(short_code=code).first()
        if not existing:
            return code

@router.post("/shorten", response_model=schemas.LinkOut)
def create_short_link(link_data: schemas.LinkCreate,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(auth.get_current_user_optional)):

    owner_id = current_user.id if current_user else None
    alias = link_data.alias
    if alias:
        existing = db.query(models.Link).filter_by(short_code=alias).first()
        if existing:
            raise HTTPException(status_code=400, detail="Указанный alias уже занят")
        short_code = alias
    else:
        short_code = generate_unique_code(db)
    new_link = models.Link(
        original_url=link_data.original_url,
        short_code=short_code,
        expires_at=link_data.expires_at,
        owner_id=owner_id,
        project_id=link_data.project_id
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link

@router.get("/{short_code}/stats", response_model=schemas.LinkOut)
def get_link_stats(short_code: str,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    link = db.query(models.Link).filter_by(short_code=short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    if link.owner_id:
        if link.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Доступ запрещен")
    else:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return link

@router.get("/search", response_model=List[schemas.LinkOut])
def search_links(original_url: str,
                 db: Session = Depends(get_db),
                 current_user: models.User = Depends(auth.get_current_user)):
    links_query = db.query(models.Link).filter(models.Link.owner_id == current_user.id)
    results = links_query.filter(models.Link.original_url.ilike(f"%{original_url}%")).all()
    return results

@router.put("/{short_code}", response_model=schemas.LinkOut)
def update_link(short_code: str,
                data: schemas.LinkUpdate,
                db: Session = Depends(get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    link = db.query(models.Link).filter_by(short_code=short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    if link.owner_id:
        if link.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Доступ запрещен")
    else:

        raise HTTPException(status_code=403, detail="Доступ запрещен")

    if data.original_url is not None:
        link.original_url = data.original_url
    if data.expires_at is not None:
        link.expires_at = data.expires_at
    if data.alias:
        new_code = data.alias
        if new_code != short_code:
            if db.query(models.Link).filter_by(short_code=new_code).first():
                raise HTTPException(status_code=400, detail="Указанный alias уже занят")
            link.short_code = new_code
    if data.project_id is not None:
        link.project_id = data.project_id
    db.commit()
    db.refresh(link)
    return link

@router.delete("/{short_code}", status_code=204)
def delete_link(short_code: str,
                db: Session = Depends(get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    link = db.query(models.Link).filter_by(short_code=short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    if link.owner_id:
        if link.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Доступ запрещен")
    else:
    
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    db.delete(link)
    db.commit()

    return Response(status_code=204)

@router.get("/expired", response_model=List[schemas.LinkOut])
def list_expired_links(db: Session = Depends(get_db),
                       current_user: models.User = Depends(auth.get_current_user)):
    expired_links = db.query(models.Link).filter(
        models.Link.owner_id == current_user.id,
        models.Link.is_active == False
    ).all()
    return expired_links
