from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from .schemas import UserCreate, UserResponse, LoginRequest, LoginResponse, UserUpdate
from .service import UserService
from .repository import UserRepository
from App.core.mysql import get_db
from App.middlewares.auth import get_current_user

router = APIRouter()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    repo = UserRepository(db)
    return UserService(repo)

@router.get("/", response_model=List[UserResponse])
def list_users(service: UserService = Depends(get_user_service)):
    return service.get_users()

@router.get("/me", response_model=UserResponse)
def get_me(
    service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    # Devuelve el usuario autenticado
    return service.get_user_by_id(current_user["id_user"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return service.register_user(data)

@router.post("/login", response_model=LoginResponse)
def login_user(
    data: LoginRequest,
    service: UserService = Depends(get_user_service)
):
    return service.login_user(data.email, data.password)

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    service.delete_user(current_user["id_user"])
    return {"detail": "User deleted successfully"}

@router.put("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    return service.update_user(current_user["id_user"], data, data.current_password)