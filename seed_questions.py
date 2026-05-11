import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.modules.users.models import User
from app.modules.friendship.models import Question

async def seed():
    engine = create_async_engine(str(settings.DATABASE_URL))
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    questions = [
        {"text": "Mening sevimli rangim?", "options": ["Qora", "Oq", "Qizil", "Ko'k"]},
        {"text": "Men ko'proq qaysi ovqatni yoqtiraman?", "options": ["Osh", "Shashlik", "Fast food", "Manti"]},
        {"text": "Men bo'sh vaqtimda nima qilaman?", "options": ["Kino ko'rish", "Kitob o'qish", "O'yin", "Uxlash"]},
        {"text": "Mening orzu davlatim qaysi?", "options": ["AQSh", "Yaponiya", "Yevropa", "Dubay"]},
        {"text": "Men ertalabmi yoki kechasi faolman?", "options": ["Ertalab", "Kechasi", "Ikkalasi", "Dangasa"]},
        {"text": "Men introvertmanmi yoki extravert?", "options": ["Introvert", "Extravert", "Ambivert", "Bilmayman"]},
        {"text": "Men nimadan ko'proq qo'rqaman?", "options": ["Yolg'izlik", "Balandlik", "Hasharot", "Qorong'ulik"]},
        {"text": "Men qaysi faslni yaxshi ko'raman?", "options": ["Bahor", "Yoz", "Kuz", "Qish"]},
        {"text": "Men uchun eng muhim narsa nima?", "options": ["Oila", "Do'stlar", "Pul", "Karyera"]},
        {"text": "Men stress paytida nima qilaman?", "options": ["Ovqat", "Musiqa", "Uxlash", "Asabiylashish"]},
    ]
    
    async with async_session() as session:
        for q in questions:
            question = Question(text=q["text"], options=q["options"])
            session.add(question)
        await session.commit()
    print("Database seeded with 10 questions successfully.")

if __name__ == "__main__":
    asyncio.run(seed())
