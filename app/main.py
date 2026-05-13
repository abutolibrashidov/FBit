import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.config import settings
from bot.handlers import setup_handlers
from api.admin import admin_router

# Logging setup
logging.basicConfig(level=settings.LOG_LEVEL, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Initialize Bot and Dispatcher
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

from contextlib import asynccontextmanager


# FastAPI lifespan for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup handlers
    setup_handlers(dp)
    
    # Set Telegram webhook
    webhook_url = f"{settings.BASE_URL}/webhook"
    await bot.set_webhook(webhook_url, drop_pending_updates=True)
    logger.info(f"Bot webhook set to: {webhook_url}")
    
    yield
    
    # Shutdown
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("Application shut down and webhook deleted.")

# FastAPI setup
app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://fbitbot.netlify.app",
    "https://fbit-1.onrender.com",
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/admin")

@app.get("/")
async def root():
    return {"status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Endpoint for Telegram Webhook updates."""
    try:
        update_data = await request.json()
        update = Update.model_validate(update_data)
        await dp.feed_update(bot, update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/health")
async def health_check():
    return {"status": "alive"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
