from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List

# ---------- User ----------
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

class UserOut(UserBase):
    id: int
    class Config:
        from_attributes = True

# ---------- Auth ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

# ---------- Project ----------
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None

class ProjectOut(ProjectBase):
    id: int
    class Config:
        from_attributes = True

# ---------- Task ----------
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    done: Optional[bool] = False
    project_id: int

    @validator("title")
    def title_trim(cls, v):
        if v.strip() == "":
            raise ValueError("Title cannot be empty/whitespace")
        return v.strip()

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    done: Optional[bool] = None
    project_id: Optional[int] = None

class TaskOut(TaskBase):
    id: int
    class Config:
        from_attributes = True

# ---------- Pagination ----------
class PageParams(BaseModel):
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)

class Page(BaseModel):
    total: int
    items: list
