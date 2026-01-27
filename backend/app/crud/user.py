from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models import user as user_model
from backend.app.schemas import user as user_schema

class CRUDUser:
    async def create_user(self, db: AsyncSession, user: user_schema.UserCreate) -> user_model.User:
        # Check if user exists
        result = await db.execute(select(user_model.User).filter(user_model.User.user_name == user.user_name))
        db_user = result.scalars().first()
        
        if db_user:
            # Update SESSDATA
            db_user.sessdata = user.sessdata
        else:
            # Create new user
            db_user = user_model.User(**user.model_dump())
            db.add(db_user)
            
        await db.flush()
        return db_user

    async def get_user_by_name(self, db: AsyncSession, user_name: str) -> user_model.User | None:
        result = await db.execute(select(user_model.User).filter(user_model.User.user_name == user_name))
        return result.scalars().first()

    async def delete_user_by_name(self, db: AsyncSession, user_name: str) -> bool:
        """
        根据用户名删除用户

        Args:
            db (AsyncSession): 数据库会话
            user_name (str): 用户名称

        Returns:
            bool: 是否删除成功
        """
        result = await db.execute(select(user_model.User).filter(user_model.User.user_name == user_name))
        db_user = result.scalars().first()
        if db_user:
            await db.delete(db_user)
            await db.flush()
            return True
        return False

crud_user = CRUDUser()
