from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session  
from datetime import datetime, timedelta
import os
import redis
import threading, time
from sqlalchemy import or_

from app.database import Base, engine, SessionLocal, get_db
from app import models, auth
from app.routers import auth as auth_router, links as links_router, projects as projects_router

from datetime import datetime, timezone, timedelta

app = FastAPI()

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(links_router.router, prefix="/links", tags=["links"])
app.include_router(projects_router.router, prefix="/projects", tags=["projects"])

@app.get("/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    link = db.query(models.Link).filter_by(short_code=short_code).first()
    if not link or not link.is_active:
        raise HTTPException(status_code=404, detail="Ссылка не найдена или неактивна")
    if link.expires_at and datetime.now(timezone.utc) > link.expires_at:
        link.is_active = False
        db.commit()
        raise HTTPException(status_code=404, detail="Срок действия ссылки истек")
    cached_url = redis_client.get(short_code)
    if cached_url:
        target_url = cached_url
    else:
        target_url = link.original_url
    link.click_count += 1
    link.last_click_at = datetime.now(timezone.utc)
    db.commit()
    if link.click_count == 10:
        redis_client.set(short_code, link.original_url)
    return RedirectResponse(url=target_url)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    def cleanup_job():
        while True:
            time.sleep(86400)  
            db = SessionLocal()
            try:
              
                days = int(os.getenv("CLEANUP_DAYS", 30))
                cutoff_date = datetime.utcnow() - timedelta(days=days)
              
                links_to_deactivate = db.query(models.Link).filter(
                    models.Link.is_active == True,
                    or_(
                        models.Link.last_click_at < cutoff_date,
                        (models.Link.last_click_at.is_(None) & (models.Link.created_at < cutoff_date))
                    )
                ).all()
                for l in links_to_deactivate:
                    l.is_active = False
                db.commit()
            finally:
                db.close()

    threading.Thread(target=cleanup_job, daemon=True).start()
