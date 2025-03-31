from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class LinkBase(BaseModel):
    original_url: HttpUrl
    alias: Optional[str] = None      
    expires_at: Optional[datetime] = None 
    project_id: Optional[int] = None  

class LinkCreate(LinkBase):
    pass 

class LinkUpdate(BaseModel):
    original_url: Optional[HttpUrl] = None
    alias: Optional[str] = None
    expires_at: Optional[datetime] = None
    project_id: Optional[int] = None

class LinkOut(BaseModel):
    short_code: str
    original_url: HttpUrl
    created_at: datetime
    expires_at: Optional[datetime] = None
    click_count: int
    last_click_at: Optional[datetime] = None
    owner_id: Optional[int] = None
    project_id: Optional[int] = None
    class Config:
        orm_mode = True

class ProjectCreate(BaseModel):
    name: str

class ProjectOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True
