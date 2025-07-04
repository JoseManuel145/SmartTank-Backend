from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    id_user: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    model_config = {
        "from_attributes": True
    }

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id_user: str
    
class UserUpdate(BaseModel):
    current_password: str
    email: Optional[EmailStr] = None
    password: Optional[str] = None
