from pydantic import BaseModel, EmailStr


# ==========================
# User Schemas
# ==========================

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# ==========================
# File Schemas
# ==========================

class FileResponse(BaseModel):
    id: int
    filename: str
    filepath: str

    class Config:
        from_attributes = True