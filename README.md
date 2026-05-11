# Telegram Teen Social Ecosystem

Scalable Telegram-native platform for Uzbek teenagers.

## Features
- **Anonymous Inbox**: Personal links for anonymous messages.
- **Friendship Score**: Social tests to measure friend compatibility.
- **Anonymous Polls**: Templates for peer feedback and interaction.
- **Analytics**: Event-driven tracking system.
- **Admin Panel**: Backend APIs for system monitoring.

## Tech Stack
- Python 3.12+
- FastAPI & Aiogram 3
- PostgreSQL & SQLAlchemy Async
- Alembic for migrations
- Redis for FSM
- Docker & Docker Compose

## Setup Instructions

### 1. Environment Configuration
Copy `.env.example` to `.env` and fill in your details:
```bash
cp .env.example .env
```

### 2. Run with Docker
```bash
docker-compose up --build
```

### 3. Database Migrations
```bash
docker-compose exec bot alembic upgrade head
```

### 4. Seed Data
```bash
docker-compose exec bot python seed.py
```

## Uzbekistan UX
All user-facing content is localized in Uzbek (`app/core/texts.py`).

## Architecture
Modular clean architecture allows easy addition of new features like streaks, communities, etc.
