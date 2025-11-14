import yt_dlp
import os
import time
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
from config import TWITCH_CHANNEL, VIDEO_DIR, GENERATE_SYNTHETIC_CHAT, CHAT_MESSAGES_PER_VIDEO, LOG_FILE
from models import db, TwitchStream, ChatMessage, ArchiveStats

# Логирование
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TwitchArchiver:
    """Архиватор VOD с чата Twitch"""
    
    def __init__(self, channel_name=TWITCH_CHANNEL):
        self.channel_name = channel_name.lower()
        self.base_url = f"https://www.twitch.tv/{self.channel_name}"
        logger.info(f"🎮 Инициализация архиватора для канала: {self.channel_name}")
    
    def get_channel_vods(self, limit=50):
        """Получает список VOD с канала"""
        logger.info(f"📺 Ищу VOD для канала {self.channel_name}...")
        
        url = f"{self.base_url}/videos?filter=uploads"
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'socket_timeout': 30,
        }
        
        vods_list = []
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                entries = info.get('entries', [])[:limit]
                
                for entry in entries:
                    vod_info = {
                        'id': entry.get('id'),
                        'title': entry.get('title', 'Unknown'),
                        'description': entry.get('description', ''),
                        'upload_date': entry.get('upload_date'),
                        'duration': entry.get('duration', 0),
                        'thumbnail': entry.get('thumbnail'),
                        'url': f"https://www.twitch.tv/videos/{entry.get('id')}",
                    }
                    vods_list.append(vod_info)
                
                logger.info(f"✅ Найдено {len(vods_list)} VOD")
                print(f"✅ Найдено {len(vods_list)} VOD")
                return vods_list
        
        except Exception as e:
            logger.error(f"❌ Ошибка при получении VOD: {e}")
            print(f"❌ Ошибка: {e}")
            return []
    
    def download_vod(self, vod_id, vod_title):
        """Скачивает один VOD"""
        logger.info(f"⬇️  Скачиваю: {vod_title}")
        print(f"⬇️  Скачиваю: {vod_title}")
        
        url = f"https://www.twitch.tv/videos/{vod_id}"
        
        # Безопасное имя файла
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in vod_title).rstrip()[:100]
        video_filename = f"{safe_title}_{vod_id}.mp4"
        video_path = os.path.join(VIDEO_DIR, video_filename)
        
        # Если уже скачано, пропускаем
        if os.path.exists(video_path):
            logger.info(f"⏭️  Видео уже скачано: {video_path}")
            print(f"⏭️  Видео уже существует")
            return video_path
        
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': os.path.join(VIDEO_DIR, '%(title)s_%(id)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'socket_timeout': 30,
            'progress_hooks': [self._progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                logger.info(f"✅ Скачано: {filename}")
                print(f"✅ Скачано успешно!")
                return filename
        except Exception as e:
            logger.error(f"❌ Ошибка при скачивании: {e}")
            print(f"❌ Ошибка при скачивании: {e}")
            return None
    
    def _progress_hook(self, d):
        """Прогресс скачивания"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            print(f"  Прогресс: {percent} на скорости {speed}")
    
    def generate_synthetic_chat(self, duration_seconds):
        """Генерирует примерный чат"""
        logger.info(f"🤖 Генерирую синтетический чат ({duration_seconds}с)...")
        
        sample_messages = [
            "Привет!",
            "Спасибо за стрим!",
            "Класс!",
            "Еще!",
            "Супер контент",
            "Интересно",
            "Лучший!",
            "Жду продолжения",
            "Отлично!",
            "Спасибо!",
            "Продолжай так!",
            "Давай еще!",
            "Как хорошо!",
            "Стрим огонь!",
            "Все понимают?",
            "Согласен!",
            "Я с вами!",
            "Невероятно!",
            "Wow!",
            "Yes!",
        ]
        
        usernames = [
            f"viewer_{i}" for i in range(1, 100)
        ]
        
        messages = []
        
        # Генерируем примерно 1 сообщение в минуту
        message_count = max(10, int(duration_seconds / 60))
        
        for _ in range(message_count):
            msg_time = random.randint(0, int(duration_seconds))
            messages.append({
                'username': random.choice(usernames),
                'message': random.choice(sample_messages),
                'time_seconds': msg_time,
                'timestamp': datetime.now() - timedelta(seconds=duration_seconds - msg_time),
                'is_mod': random.choice([False, False, False, True]),  # 25% модераторов
                'is_sub': random.choice([False, False, False, False, True]),  # 20% подписчиков
                'is_broadcaster': False,
            })
        
        # Сортируем по времени
        messages.sort(key=lambda x: x['time_seconds'])
        
        logger.info(f"✅ Сгенерировано {len(messages)} сообщений чата")
        return messages
    
    def save_stream_to_db(self, vod_info, video_path):
        """Сохраняет стрим в БД"""
        logger.info(f"💾 Сохраняю в БД: {vod_info['title']}")
        
        # Проверяем, не существует ли уже
        existing = TwitchStream.query.filter_by(twitch_video_id=vod_info['id']).first()
        if existing:
            logger.info(f"⏭️  Стрим уже в БД: {existing.id}")
            return existing.id
        
        # Форматируем дату
        if vod_info.get('upload_date'):
            stream_date = datetime.strptime(vod_info['upload_date'], '%Y%m%d')
        else:
            stream_date = datetime.now()
        
        # Форматируем длительность
        duration = vod_info.get('duration', 0)
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        stream = TwitchStream(
            twitch_video_id=vod_info['id'],
            title=vod_info['title'],
            description=vod_info.get('description', ''),
            channel_name=self.channel_name,
            stream_date=stream_date,
            duration_seconds=duration,
            duration_formatted=duration_formatted,
            video_url=vod_info['url'],
            local_video_path=video_path,
            thumbnail_url=vod_info.get('thumbnail', ''),
            is_downloaded=True,
        )
        
        db.session.add(stream)
        db.session.commit()
        
        logger.info(f"✅ Сохранено в БД: ID {stream.id}")
        return stream.id
    
    def save_chat_to_db(self, stream_id, messages):
        """Сохраняет сообщения чата в БД"""
        logger.info(f"💬 Сохраняю {len(messages)} сообщений чата...")
        
        for msg in messages:
            # Форматируем время
            time_seconds = msg['time_seconds']
            hours = int(time_seconds // 3600)
            minutes = int((time_seconds % 3600) // 60)
            seconds = int(time_seconds % 60)
            time_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            chat_msg = ChatMessage(
                stream_id=stream_id,
                username=msg['username'],
                message_text=msg['message'],
                message_time_seconds=time_seconds,
                message_time_formatted=time_formatted,
                message_timestamp=msg['timestamp'],
                is_moderator=msg.get('is_mod', False),
                is_subscriber=msg.get('is_sub', False),
                is_broadcaster=msg.get('is_broadcaster', False),
            )
            db.session.add(chat_msg)
        
        db.session.commit()
        logger.info(f"✅ Сохранено {len(messages)} сообщений")
        
        # Обновляем счётчик в стриме
        stream = TwitchStream.query.get(stream_id)
        stream.chat_message_count = len(messages)
        stream.chat_is_synthetic = True
        db.session.commit()
    
    def archive_stream(self, vod_id, vod_title, vod_info):
        """Полный процесс: скачивание + сохранение чата"""
        print(f"\n{'='*60}")
        print(f"📺 Архивирование: {vod_title}")
        print(f"{'='*60}")
        
        # Скачиваем видео
        video_path = self.download_vod(vod_id, vod_title)
        if not video_path:
            logger.error(f"❌ Не удалось скачать {vod_title}")
            return None
        
        # Сохраняем информацию о стриме в БД
        stream_id = self.save_stream_to_db(vod_info, video_path)
        
        # Генерируем/восстанавливаем чат
        if GENERATE_SYNTHETIC_CHAT:
            duration = vod_info.get('duration', 3600)
            chat_messages = self.generate_synthetic_chat(duration)
            self.save_chat_to_db(stream_id, chat_messages)
        
        logger.info(f"✅ Архивирование завершено!")
        print(f"✅ Архивирование завершено!\n")
        
        return stream_id
    
    def sync_all_vods(self, limit=10):
        """Синхронизирует все VOD с каналаа"""
        logger.info(f"🔄 Начало синхронизации канала {self.channel_name}...")
        print(f"\n{'='*60}")
        print(f"🔄 СИНХРОНИЗАЦИЯ КАНАЛА {self.channel_name.upper()}")
        print(f"{'='*60}\n")
        
        vods = self.get_channel_vods(limit=limit)
        
        if not vods:
            logger.warning("⚠️  VOD не найдены")
            print("⚠️  VOD не найдены")
            return 0
        
        archived_count = 0
        
        for i, vod in enumerate(vods, 1):
            print(f"\n[{i}/{len(vods)}]", end=" ")
            
            # Проверяем, не архивирован ли уже
            existing = TwitchStream.query.filter_by(twitch_video_id=vod['id']).first()
            if existing:
                print(f"⏭️  Уже архивирован")
                continue
            
            try:
                self.archive_stream(vod['id'], vod['title'], vod)
                archived_count += 1
                time.sleep(2)  # Задержка между скачиваниями
            except Exception as e:
                logger.error(f"❌ Ошибка при архивировании {vod['id']}: {e}")
                print(f"❌ Ошибка: {e}")
                continue
        
        logger.info(f"✅ Синхронизация завершена! Архивировано {archived_count} новых VOD")
        print(f"\n{'='*60}")
        print(f"✅ Синхронизация завершена!")
        print(f"📊 Архивировано: {archived_count} новых видео")
        print(f"{'='*60}\n")
        
        return archived_count
