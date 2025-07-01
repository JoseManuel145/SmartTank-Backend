from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from App.users.model import User
from App.core.mysql import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

load_dotenv()

# Obtiene los valores de las variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = HTTPBearer()

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "sub" not in payload:
            raise ValueError("Invalid token payload")
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

def get_current_user(db: Session = Depends(get_db),
                           token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    payload = verify_token(token.credentials)
    id_user = str(payload.get("sub"))
    email = payload.get("email")
    user_query = db.execute(select(User).filter(User.id_user == id_user))
    user = user_query.first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id_user": id_user,
        "email": email,
    }
    
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt