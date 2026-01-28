from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models.auth import Auth as Auth_model
from backend.app.schemas.auth import  UserInfo

class CRUDAuth:

    async def create_user(self, db: AsyncSession, user: UserInfo) -> Auth_model:
        # 优先通过 UID 查找
        db_user = None
        if user.uid:
            result = await db.execute(select(Auth_model).filter(Auth_model.uid == user.uid))
            db_user = result.scalars().first()
        
        # 如果没有 UID，尝试通过用户名查找 (兼容旧逻辑)
        if not db_user:
            result = await db.execute(select(Auth_model).filter(Auth_model.user_name == user.user_name))
            db_user = result.scalars().first()
        
        if db_user:
            # Update info
            db_user.user_name = user.user_name
            db_user.sessdata = user.sessdata
            if user.uid:
                db_user.uid = user.uid
            if user.face_img:
                db_user.face_img = user.face_img
            # 更新用户名，防止改名
            db_user.user_name = user.user_name
        else:
            # Create new user
            db_user = Auth_model(**user.model_dump())
            db.add(db_user)
            
        await db.flush()
        return db_user

    async def get_user_by_uid(self, db: AsyncSession, uid: str) -> Auth_model | None:
        result = await db.execute(select(Auth_model).filter(Auth_model.uid == uid))
        return result.scalars().first()


    async def get_user_by_name(self, db: AsyncSession, user_name: str) -> Auth_model | None:
        result = await db.execute(select(Auth_model).filter(Auth_model.user_name == user_name))
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
        result = await db.execute(select(Auth_model).filter(Auth_model.user_name == user_name))
        db_user = result.scalars().first()
        if db_user:
            await db.delete(db_user)
            await db.flush()
            return True
        return False

crud_auth = CRUDAuth()
