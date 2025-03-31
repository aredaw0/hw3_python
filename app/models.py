from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Relationships
    links = relationship("Link", back_populates="owner", cascade="all, delete")
    projects = relationship("Project", back_populates="user", cascade="all, delete")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # Relationships
    user = relationship("User", back_populates="projects")
    links = relationship("Link", back_populates="project", cascade="all, delete")

class Link(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(String(50), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    click_count = Column(Integer, default=0)
    last_click_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"))
    # Relationships
    owner = relationship("User", back_populates="links")
    project = relationship("Project", back_populates="links")

