import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models import Base, User, Admin, Account
from app.auth import get_password_hash
from app.config import config, DATABASE_URL

async def run_migration():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created")
    
    async with async_session_maker() as session:
        test_user = User(
            email='testuser@example.com',
            full_name='Test User',
            hashed_password=get_password_hash('password123')
        )
        session.add(test_user)
        await session.flush()
        
        test_account = Account(user_id=test_user.id, balance=0)
        session.add(test_account)
        
        test_admin = Admin(
            email='admin@example.com',
            full_name='Test Admin',
            hashed_password=get_password_hash('admin123')
        )
        session.add(test_admin)
        
        await session.commit()
        print("Test data created")
        print(f"Test user created: id={test_user.id}, email={test_user.email}")
        print(f"Test account created: id={test_account.id}, user_id={test_account.user_id}")
        print(f"Test admin created: id={test_admin.id}, email={test_admin.email}")
    
    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(run_migration())