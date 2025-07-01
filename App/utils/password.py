import bcrypt

def hash_password(password: str) -> str:
    #Hashea una contraseña en texto plano y devuelve el hash.
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()

def verify_password(password: str, hashed_password: str) -> bool:
    #Verifica si la contraseña coincide con el hash almacenado.
    return bcrypt.checkpw(password.encode(), hashed_password.encode())