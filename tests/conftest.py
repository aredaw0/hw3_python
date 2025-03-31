import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

# Используем SQLite для тестов — in-memory (или файл)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine_test = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """
    Создаём таблицы один раз на сессию тестов.
    Затем после тестов (yield) всё дропаем.
    """
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)

def override_get_db():
    """Функция, переопределяющая зависимость get_db в приложении на нашу тестовую БД."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Переопределяем зависимость в нашем FastAPI-приложении.
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture()
def client():
    """Фикстура для fastapi.testclient.TestClient."""
    with TestClient(app) as c:
        yield c
