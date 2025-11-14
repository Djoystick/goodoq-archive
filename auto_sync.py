import time
import schedule
import logging
from config import (
    TWITCH_CHANNEL, AUTO_SYNC_INTERVAL_HOURS, 
    AUTO_SYNC_ENABLED, MAX_VIDEOS_PER_SYNC, LOG_FILE
)
from app import app
from twitch_scraper import TwitchArchiver
from models import db, ArchiveStats
from datetime import datetime, timedelta

# Логирование
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def sync_job():
    """Задача синхронизации"""
    logger.info("="*60)
    logger.info("🔄 АВТОМАТИЧЕСКАЯ СИНХРОНИЗАЦИЯ НАЧАТА")
    logger.info("="*60)
    print("\n🔄 АВТОМАТИЧЕСКАЯ СИНХРОНИЗАЦИЯ НАЧАЛАСЬ...")
    
    with app.app_context():
        try:
            archiver = TwitchArchiver(TWITCH_CHANNEL)
            archived = archiver.sync_all_vods(limit=MAX_VIDEOS_PER_SYNC)
            
            # Обновляем статистику
            stats = ArchiveStats.query.filter_by(channel_name=TWITCH_CHANNEL).first()
            if not stats:
                stats = ArchiveStats(channel_name=TWITCH_CHANNEL)
                db.session.add(stats)
            
            stats.last_sync = datetime.now()
            stats.next_sync = datetime.now() + timedelta(hours=AUTO_SYNC_INTERVAL_HOURS)
            db.session.commit()
            
            logger.info(f"✅ Синхронизация завершена! Архивировано: {archived} видео")
            print(f"✅ Синхронизация завершена! Архивировано: {archived} видео\n")
        
        except Exception as e:
            logger.error(f"❌ Ошибка при синхронизации: {e}")
            print(f"❌ Ошибка: {e}\n")

def start_scheduler():
    """Запускает планировщик"""
    if not AUTO_SYNC_ENABLED:
        logger.warning("⚠️  Автоматическая синхронизация отключена")
        print("⚠️  Автоматическая синхронизация отключена")
        return
    
    logger.info(f"🕐 Планировщик запущен (синхронизация каждые {AUTO_SYNC_INTERVAL_HOURS} часов)")
    print(f"🕐 Планировщик запущен (синхронизация каждые {AUTO_SYNC_INTERVAL_HOURS} часов)")
    
    # Запускаем синхронизацию сразу при запуске
    print("📺 Выполняю начальную синхронизацию...")
    sync_job()
    
    # Затем по расписанию
    schedule.every(AUTO_SYNC_INTERVAL_HOURS).hours.do(sync_job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Проверяем каждую минуту

if __name__ == "__main__":
    logger.info("🚀 ЗАПУСК АВТОМАТИЧЕСКОГО СИНХРОНИЗАТОРА")
    print("🚀 ЗАПУСК АВТОМАТИЧЕСКОГО СИНХРОНИЗАТОРА АРХИВА")
    print(f"📺 Канал: {TWITCH_CHANNEL}")
    print(f"🕐 Интервал: каждые {AUTO_SYNC_INTERVAL_HOURS} часов")
    
    start_scheduler()
