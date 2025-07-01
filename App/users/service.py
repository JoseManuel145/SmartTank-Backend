from .repository import UserRepository
from .schemas import UserCreate, UserResponse, UserUpdate, LoginResponse
from App.middlewares.auth import create_access_token
from typing import List
from App.utils import uuid, password

class UserService:
    def __init__(self, repository: UserRepository):
        self.repo = repository

    # Funcion validad solo para depurar usuarios
    def get_users(self) -> List[UserResponse]:
        # Obtiene todos los usuarios
        users = self.repo.get_all()
        return [UserResponse.from_orm(u) for u in users]

    def get_user_by_id(self, id_user: str) -> UserResponse:
        # Obtiene un usuario por su ID
        user = self.repo.get_by_id(id_user)
        if not user:
            raise ValueError("User not found")
        return UserResponse.from_orm(user)

    def register_user(self, data: UserCreate) -> LoginResponse:
        # Genera un UUID para el nuevo usuario y hashea la contraseña
        id = uuid.generate_uuid()
        hashed_password = password.hash_password(data.password)
        # Crea una copia del modelo con los datos actualizados
        user_data = data.model_copy(update={"password": hashed_password, "id_user": id})
        user = self.repo.create(user_data)
        
        token = create_access_token({"sub": user.id_user})
        return LoginResponse(user=UserResponse.from_orm(user), access_token=token)

    def login_user(self, email: str, password_request: str) -> LoginResponse:
        # Obtiene el usuario por email
        user = self.repo.get_by_email(email)
        # Comprueba si el usuario existe y si la contraseña es correcta
        if not user or not password.verify_password(password_request, user.password):
            raise ValueError("Invalid email or password")
        
        token = create_access_token({"sub": user.id_user})
        return LoginResponse(user=UserResponse.from_orm(user), access_token=token)

    def update_user(self, id_user: str, data: UserUpdate, current_password: str) -> UserResponse:
        # Busca el usuario existente
        user = self.repo.get_by_id(id_user)
        if not user:
            raise ValueError("User not found")
        # Verifica la contraseña actual
        if not password.verify_password(current_password, user.password):
            raise ValueError("Current password is incorrect")
        # Actualiza los datos del usuario
        update_data = data.model_dump(exclude_unset=True)
        # Si hay una nueva contraseña, hashearla antes de guardar
        if "password" in update_data and update_data["password"]:
            update_data["password"] = password.hash_password(update_data["password"])
        updated_user = self.repo.update(id_user, update_data)
        return UserResponse.from_orm(updated_user)
    
    def delete_user(self, id_user: str) -> bool:
        # Elimina un usuario por su ID
        user = self.repo.get_by_id(id_user)
        if not user:
            raise ValueError("User not found")
        return self.repo.delete(id_user)