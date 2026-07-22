from database.database import SessionLocal
from database import crud
from database.schemas import UserCreate


db = SessionLocal()

user = UserCreate(
    username="Maheshwari",
    email="maheshwari@gmail.com",
    password="123456"
)

crud.create_user(db, user)

print("Database Working Successfully")