import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.modules.users.models import User
from app.modules.polls.models import PollTemplate

async def seed():
    engine = create_async_engine(str(settings.DATABASE_URL))
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    templates = [
        {"q": "Kim ko'proq kulgili?", "cat": "Fun"},
        {"q": "Kim ko'proq muvaffaqiyatli bo'ladi?", "cat": "Future"},
        {"q": "Men haqimda nima deb o'ylaysan?", "cat": "Personality"},
        {"q": "Meni 1-10 da bahola", "cat": "Personality"}
    ]
    
    async with async_session() as session:
        for t in templates:
            poll = PollTemplate(question_text=t["q"], category=t["cat"])
            session.add(poll)
        await session.commit()
    print("Poll templates seeded!")

if __name__ == "__main__":
    asyncio.run(seed())
