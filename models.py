from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class TwitchStream(db.Model):
    """Модель стрима"""
    __tablename__ = 'streams'
    
    id = db.Column(db.Integer, primary_key=True)
    twitch_video_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    channel_name = db.Column(db.String(200), nullable=False)
    stream_date = db.Column(db.DateTime, nullable=False, index=True)
    duration_seconds = db.Column(db.Integer, default=0)
    duration_formatted = db.Column(db.String(20))
    
    # Пути
    video_url = db.Column(db.String(1000))
    local_video_path = db.Column(db.String(1000))
    thumbnail_url = db.Column(db.String(1000))
    
    # Статусы
    is_downloaded = db.Column(db.Boolean, default=False, index=True)
    is_processed = db.Column(db.Boolean, default=False)
    
    # Чат
    chat_message_count = db.Column(db.Integer, default=0)
    chat_is_synthetic = db.Column(db.Boolean, default=False)  # Сгенерирован ли чат
    
    # Статистика
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    
    # Служебное
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    chat_messages = db.relationship('ChatMessage', backref='stream', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TwitchStream {self.title[:30]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'channel': self.channel_name,
            'date': self.stream_date.isoformat(),
            'duration': self.duration_formatted,
            'messages': self.chat_message_count,
            'is_downloaded': self.is_downloaded,
        }


class ChatMessage(db.Model):
    """Модель сообщения чата"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    stream_id = db.Column(db.Integer, db.ForeignKey('streams.id'), nullable=False, index=True)
    
    username = db.Column(db.String(200), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    
    # Время в видео (в секундах от начала)
    message_time_seconds = db.Column(db.Float, nullable=False)
    message_time_formatted = db.Column(db.String(20))
    
    # Реальное время сообщения
    message_timestamp = db.Column(db.DateTime)
    
    # Флаги пользователя
    is_moderator = db.Column(db.Boolean, default=False)
    is_subscriber = db.Column(db.Boolean, default=False)
    is_broadcaster = db.Column(db.Boolean, default=False)
    
    # Служебное
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<ChatMessage {self.username}: {self.message_text[:20]}>'
    
    def to_dict(self):
        return {
            'username': self.username,
            'text': self.message_text,
            'time': self.message_time_seconds,
            'time_formatted': self.message_time_formatted,
            'is_mod': self.is_moderator,
            'is_sub': self.is_subscriber,
            'is_broadcaster': self.is_broadcaster,
        }


class ArchiveStats(db.Model):
    """Статистика архива"""
    __tablename__ = 'stats'
    
    id = db.Column(db.Integer, primary_key=True)
    channel_name = db.Column(db.String(200), unique=True, nullable=False)
    total_videos = db.Column(db.Integer, default=0)
    total_messages = db.Column(db.Integer, default=0)
    total_size_gb = db.Column(db.Float, default=0)
    total_duration_hours = db.Column(db.Float, default=0)
    last_sync = db.Column(db.DateTime)
    next_sync = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ArchiveStats {self.channel_name}>'
