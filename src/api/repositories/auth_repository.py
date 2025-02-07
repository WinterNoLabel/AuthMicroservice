from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.session import get_session
from fastapi import Depends
from models import User

class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_user_from_token(self, id: int, username: str):
        result = await self.session.execute(
            select(User)
            .where(User.id == id, User.username == username)
        )
        return result.scalar_one_or_none()


    async def get_user_by_phone_number(self, username: str):
        result = await self.session.execute(
            select(User)
            .where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create_user(self, model: User):
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model


def get_auth_repository(session: AsyncSession = Depends(get_session)):
    return AuthRepository(session)
