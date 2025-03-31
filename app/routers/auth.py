from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db

router = APIRouter()

@router.post("/register", response_model=schemas.UserOut)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Проверяем, что имя пользователя свободно
    existing_user = db.query(models.User).filter_by(username=user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    # Создаем нового пользователя
    hashed_pw = auth.get_password_hash(user_data.password)
    new_user = models.User(username=user_data.username, password_hash=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login_user(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    # Ищем пользователя по имени
    user = db.query(models.User).filter_by(username=user_data.username).first()
    if not user or not auth.verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    # Генерируем JWT-токен
    access_token = auth.create_access_token({"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
