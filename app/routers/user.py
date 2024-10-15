from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db

from app.backend.db import Base

from typing import List, Annotated
from app.models import User
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify

# Создаем роутер с префиксом "/user" и тегом "user" для группировки связанных маршрутов
router = APIRouter(prefix="/user", tags=["user"])

@router.get("/", response_model=List[User])
async def all_users(db: Annotated[Session, Depends(get_db)]):
    stmt = select(User)  # Используем select для получения всех пользователей
    result = await db.execute(stmt)  # Выполняем запрос
    users = result.scalars().all()  # С полученного результата получаем всех пользователей
    return users

@router.get("/{user_id}", response_model=User)
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