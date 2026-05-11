import asyncio
import logging
import sys
import httpx
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.bot.handlers import setup_handlers
from app.api.admin import admin_router

# Logging setup
logging.basicConfig(level=settings.LOG_LEVEL, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Initialize Bot and Dispatcher
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

from contextlib import asynccontextmanager


async def keep_alive_loop():
    """Ping /health every 4 minutes to prevent Render free tier cold starts."""
    await asyncio.sleep(30)  # Wait for server to be fully ready
    while True:
        try:
            async with httpx.AsyncClient() as client:
                await client.get("http://localhost:8000/health", timeout=10)
            logger.debug("Keep-alive ping sent")
        except Exception:
            pass  # Fail silently
        await asyncio.sleep(240)  # 4 minutes


# FastAPI lifespan for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup
    setup_handlers(dp)
    polling_task = asyncio.create_task(dp.start_polling(bot))
    keep_alive_task = asyncio.create_task(keep_alive_loop())
    logger.info("Bot started and FastAPI app initialized.")
    yield
    # Shutdown
    await bot.session.close()
    polling_task.cancel()
    keep_alive_task.cancel()
    logger.info("Application shut down.")

# FastAPI setup
app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/admin")


@app.get("/health")
async def health_check():
    return {"status": "alive"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
