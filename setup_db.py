import asyncio
import asyncpg

async def setup():
    conn = await asyncpg.connect('postgresql://postgres:1abutolib1@localhost/postgres')
    try:
        await conn.execute('CREATE DATABASE fbit_db')
        print("Database created!")
    except Exception as e:
        print(f"Error or already exists: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(setup())
