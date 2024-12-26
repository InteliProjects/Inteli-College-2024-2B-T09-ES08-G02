import bcrypt
from sqlalchemy.orm import Session
from ..models.user import User

def create_user_service(db: Session, username: str, password: str, project: dict, name:str):
    # Verificar se o usuário já existe
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return {"error": "Username already exists"}, 400

    # Encriptar a senha
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # Criar o usuário
    new_user = User(username=username, password=hashed_password.decode("utf-8"), project=project, name=name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user": {"username": username}, "project":{"project":project}}, 201
