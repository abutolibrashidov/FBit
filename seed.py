import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import async_session, engine
from app.modules.friendship.models import Question
from app.modules.polls.models import PollTemplate

async def seed_data():
    async with async_session() as session:
        # Friendship Questions
        questions = [
            Question(
                text="Mening eng sevimli rangim qaysi?",
                options=["Qora", "Oq", "Qizil", "Ko'k"],
                correct_option_index=0
            ),
            Question(
                text="Mening eng yaxshi ko'rgan ovqatim qaysi?",
                options=["Palov", "Shashlik", "Somsa", "Pizza"],
                correct_option_index=0
            ),
            Question(
                text="Bo'sh vaqtimda nima qilishni yoqtiraman?",
                options=["Kitob o'qish", "O'yin o'ynash", "Uxlayman", "Sayohat"],
                correct_option_index=1
            )
        ]
        
        # Poll Templates
        poll_templates = [
            PollTemplate(question_text="Meni qanday tariflaysiz?"),
            PollTemplate(question_text="Mening eng katta kamchiligim nima?"),
            PollTemplate(question_text="Sizningcha, men kelajakda kim bo'laman?"),
            PollTemplate(question_text="Menga qaysi rangdagi kiyim ko'proq yarashadi?")
        ]
        
        session.add_all(questions)
        session.add_all(poll_templates)
        await session.commit()
        print("Seed data inserted successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
