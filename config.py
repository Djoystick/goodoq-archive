import os
from datetime import datetime

# ============ ТВИЧ КАНАЛ - ЕДИНСТВЕННЫЙ ПАРАМЕТР, КОТОРЫЙ НУЖНО МЕНЯТЬ ============
TWITCH_CHANNEL = "goodoq"  # <-- ВСТАВЬТЕ ИМЯ КАНАЛА СЮДА

# ============ БАЗОВЫЕ НАСТРОЙКИ ============
PROJECT_NAME = f"{TWITCH_CHANNEL.upper()} - Архив стримов"
PROJECT_DESCRIPTION = f"Архив трансляций канала {TWITCH_CHANNEL} с восстановленным чатом"

# ============ ПАПКИ И ПУТИ ============
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "static", "videos")
LOG_DIR = os.path.join(BASE_DIR, "logs")
DB_PATH = os.path.join(BASE_DIR, "database.db")

# Создаём папки если их нет
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ============ БД ============
DATABASE_URL = f"sqlite:///{DB_PATH}"

# ============ FLASK ============
SECRET_KEY = "your-secret-key-goodoq-archive-2025"
DEBUG = False

# ============ ПАРАМЕТРЫ СКАЧИВАНИЯ ============
MAX_VIDEOS_PER_SYNC = 10  # Максимум видео за один запуск
VIDEO_QUALITY = "best[ext=mp4]"  # Качество видео
GENERATE_SYNTHETIC_CHAT = True  # Генерировать синтетический чат если не найден исходный
CHAT_MESSAGES_PER_VIDEO = 100  # Примерно сообщений чата на одно видео

# ============ РАСПИСАНИЕ АВТОМАТИЗАЦИИ ============
AUTO_SYNC_INTERVAL_HOURS = 24  # Синхронизация каждые 24 часа
AUTO_SYNC_ENABLED = True  # Включить автоматическую синхронизацию

# ============ ЛОГИРОВАНИЕ ============
LOG_FILE = os.path.join(LOG_DIR, f"{TWITCH_CHANNEL}_sync.log")

# ============ API ПАРАМЕТРЫ (ПУБЛИЧНЫЕ, БЕЗ АВТОРИЗАЦИИ) ============
TWITCH_HELIX_API = "https://api.twitch.tv/helix"
TWITCH_GRAPHQL_API = "https://gql.twitch.tv/gql"
# Используем публичный Client ID из Twitch веб-приложения
TWITCH_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"

print(f"""
╔════════════════════════════════════════════════════════════╗
║         TWITCH ARCHIVE - {PROJECT_NAME}              ║
║════════════════════════════════════════════════════════════║
║  Канал: {TWITCH_CHANNEL}
║  Проект: {PROJECT_NAME}
║  БД: {DB_PATH}
║  Видео: {VIDEO_DIR}
║════════════════════════════════════════════════════════════║
""")
