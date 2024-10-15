from app.backend.db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


from fastapi import APIRouter, Depends, status, HTTPException
# Сессия БД
from sqlalchemy.orm import Session
# Функция подключения к БД
from backend.db_depends import get_db
# Аннотации, Модели БД и Pydantic.
from typing import Annotated
from models import User
from schemas import CreateUser, UpdateUser
# Функции работы с записями.
from sqlalchemy import insert, select, update, delete
# Функция создания slug-строки
from slugify import slugify



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=True)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    slug = Column(String, unique=True, index=True)

    tasks = relationship("Task", back_populates="user")

# from sqlalchemy.schema import CreateTable
# print(CreateTable(User.__table__))

router = APIRouter()


@router.get("/", response_model=List[User])
async def all_users(db: Annotated[Session, Depends(get_db)]):
    stmt = select(User)  # Используем select для получения всех пользователей
    result = await db.execute(stmt)  # Выполняем запрос
    users = result.scalars().all()  # С полученного результата получаем всех пользователей
    return users


@router.get("/user/{user_id}", response_model=User)
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    stmt = select(User).where(User.id == user_id)  # Извлечение пользователя по user_id
    result = await db.execute(stmt)
    user = result.scalars().first()  # Получаем первого пользователя из результата
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")  # Исключение в случае отсутствия пользователя
    return user


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    # Проверка на существующего пользователя
    existing_user = await db.execute(select(User).where(User.username == user.username))
    if existing_user.scalars().first():
        raise HTTPException(status_code=400, detail="User with this username already exists")

    user.slug = slugify(user.username)  # Создание slug для пользователя
    stmt = insert(User).values(**user.dict())  # Добавление нового пользователя
    await db.execute(stmt)
    await db.commit()  # Подтверждение транзакции
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put("/update/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    stmt = select(User).where(User.id == user_id)  # Извлечение пользователя по user_id
    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if existing_user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    stmt = update(User).where(User.id == user_id).values(**user.dict())  # Обновление значений пользователя
    await db.execute(stmt)
    await db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}


@router.delete("/delete/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    stmt = select(User).where(User.id == user_id)  # Извлечение пользователя по user_id
    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if existing_user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    stmt = delete(User).where(User.id == user_id)  # Удаление пользователя
    await db.execute(stmt)
    await db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User was successfully deleted'}