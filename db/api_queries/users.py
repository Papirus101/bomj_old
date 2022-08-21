import datetime
import hashlib
import random
import string

from fastapi import HTTPException

from db.models.api_user_db import Tokens, UsersApi
from api_manage.schemas import UserBase, UserCreate

from misc.services import redis

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, IntegrityError


def get_random_string(length=12):
    """ Возвращает случайную строку, которая будет использоваться в качестве соли """
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def hash_password(password: str, salt: str = None):
    """ Хеширует пароль """
    if salt is None:
        salt = get_random_string()
    enc = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100_000)
    return enc.hex()


def validate_password(password: str, hashed_password: str):
    salt, hashed = hashed_password.split('$')
    return hash_password(password, salt) == hashed


async def get_user_by_email(db_session, email: str):
    async with db_session() as session:
        sql = select(UsersApi, Tokens).join(Tokens, Tokens.owner == UsersApi.id).where(UsersApi.email == email)
        user = await session.execute(sql)
        try:
            user = user.all()
        except NoResultFound:
            return {'error': 'User not found'}
        return user[0]


async def get_user_by_token(db_session, token: str):
    async with db_session() as session:
        sql = select(UsersApi, Tokens).join(UsersApi, UsersApi.id == Tokens.owner).where(Tokens.token == token)
        data = await session.execute(sql)
        try:
            data, _ = data.one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Not Found User")
    return data


async def create_user_token(db_session, user_id: int):
    async with db_session() as session:
        token = await session.merge(Tokens(expires=datetime.datetime.now(), owner=user_id))
        await session.commit()
        return token


async def create_user(db_session, user: UserCreate):
    salt = get_random_string()
    hashed_password = hash_password(user.password, salt)
    async with db_session() as session:
        new_user = await session.merge(
            UsersApi(email=user.email, name=user.name, hashed_password=f'{salt}${hashed_password}'))
        try:
            await session.commit()
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Email or username already registered")
    token = await create_user_token(db_session, new_user.id)
    token_dict = {"token": token.token, 'exp': token.expires}

    return {**user.dict(), 'id': new_user.id, 'is_active': True, "token": token_dict}
