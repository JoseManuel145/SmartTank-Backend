from sqlalchemy.orm import Session
from typing import List
from .model import User
from .schemas import UserCreate

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[User]:
        return self.db.query(User).all()

    def get_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_id(self, id_user: str) -> User:
        return self.db.query(User).filter(User.id_user == id_user).first()
    
    def create(self, user_data: UserCreate) -> User:
        # Convertimos el esquema de entrada en una instancia del modelo User
        user = User(
            id_user=user_data.id_user,
            email=user_data.email,
            password=user_data.password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.merge(user) # Actualiza el usuario existente
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, id_user: str) -> None:
        user = self.get_by_id(id_user)
        self.db.delete(user)
        self.db.commit()
        self.db.flush()  # Asegura que los cambios se apliquen inmediatamente
        return True