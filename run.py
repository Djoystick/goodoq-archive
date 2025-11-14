#!/usr/bin/env python
"""
Главный скрипт для запуска проекта Goodoq Archive
"""

import os
import sys
import click
from app import app, db
from models import TwitchStream, ChatMessage, ArchiveStats
from twitch_scraper import TwitchArchiver
from config import TWITCH_CHANNEL, AUTO_SYNC_ENABLED, AUTO_SYNC_INTERVAL_HOURS
import logging

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ CLI КОМАНДЫ ============

@click.group()
def cli():
    """🎮 Goodoq Archive - Управление архивом стримов"""
    pass

@cli.command()
@click.option('--limit', default=10, help='Максимум видео для синхронизации')
def sync(limit):
    """🔄 Синхронизировать новые VOD с Twitch"""
    with app.app_context():
        archiver = TwitchArchiver(TWITCH_CHANNEL)
        archiver.sync_all_vods(limit=limit)

@cli.command()
def init_db():
    """📁 Инициализировать базу данных"""
    with app.app_context():
        db.create_all()
        logger.info("✅ База данных инициализирована")

@cli.command()
def clear_db():
    """🗑️  Очистить базу данных"""
    with app.app_context():
        if click.confirm('Вы уверены? Это удалит все данные!'):
            db.drop_all()
            db.create_all()
            logger.info("✅ База данных очищена")

@cli.command()
def stats():
    """📊 Показать статистику архива"""
    with app.app_context():
        total_videos = TwitchStream.query.filter_by(is_downloaded=True).count()
        total_messages = db.session.query(ChatMessage).count()
        
        print(f"""
╔════════════════════════════════════════════════════╗
║           СТАТИСТИКА АРХИВА {TWITCH_CHANNEL.upper()}           
║════════════════════════════════════════════════════╗
║  📹 Всего видео:           {total_videos}
║  💬 Всего сообщений:       {total_messages}
║════════════════════════════════════════════════════╝
        """)

@cli.command()
@click.option('--host', default='0.0.0.0', help='Host для запуска')
@click.option('--port', default=5000, help='Port для запуска')
@click.option('--debug', is_flag=True, help='Debug режим')
def run(host, port, debug):
    """▶️  Запустить веб-сервер"""
    logger.info(f"🚀 Запуск сервера на {host}:{port}")
    logger.info(f"📺 Канал: {TWITCH_CHANNEL}")
    logger.info(f"🔗 Откройте http://localhost:{port}")
    
    with app.app_context():
        db.create_all()
    
    app.run(host=host, port=port, debug=debug)

@cli.command()
def scheduler():
    """🕐 Запустить планировщик автоматической синхронизации"""
    if not AUTO_SYNC_ENABLED:
        logger.warning("⚠️  Автоматическая синхронизация отключена")
        return
    
    from auto_sync import start_scheduler
    start_scheduler()

if __name__ == '__main__':
    cli()
