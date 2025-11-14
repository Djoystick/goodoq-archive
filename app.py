from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import (
    DATABASE_URL, SECRET_KEY, DEBUG, TWITCH_CHANNEL, 
    PROJECT_NAME, PROJECT_DESCRIPTION, BASE_DIR
)
from models import db, TwitchStream, ChatMessage, ArchiveStats
import logging
from datetime import datetime
from sqlalchemy import desc

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask приложение
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG

# Инициализация
db.init_app(app)
CORS(app)

# Создаём таблицы
with app.app_context():
    db.create_all()
    logger.info("✅ БД инициализирована")

# ============ ROUTES ============

@app.route('/')
def index():
    """Главная страница"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    streams = TwitchStream.query\
        .filter_by(is_downloaded=True)\
        .order_by(desc(TwitchStream.stream_date))\
        .paginate(page=page, per_page=per_page)
    
    total_videos = TwitchStream.query.filter_by(is_downloaded=True).count()
    total_messages = db.session.query(ChatMessage).count()
    
    stats = {
        'total_videos': total_videos,
        'total_messages': total_messages,
        'channel': TWITCH_CHANNEL,
    }
    
    return render_template(
        'index.html',
        streams=streams.items,
        total_pages=streams.pages,
        current_page=page,
        stats=stats,
        project_name=PROJECT_NAME
    )

@app.route('/stream/<int:stream_id>')
def stream_view(stream_id):
    """Просмотр стрима с чатом"""
    stream = TwitchStream.query.get_or_404(stream_id)
    return render_template('stream.html', stream=stream)

@app.route('/api/streams')
def api_streams():
    """API для получения списка стримов (JSON)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    streams = TwitchStream.query\
        .filter_by(is_downloaded=True)\
        .order_by(desc(TwitchStream.stream_date))\
        .paginate(page=page, per_page=per_page)
    
    data = {
        'streams': [s.to_dict() for s in streams.items],
        'total_pages': streams.pages,
        'current_page': page,
        'total_streams': TwitchStream.query.filter_by(is_downloaded=True).count(),
        'total_messages': db.session.query(ChatMessage).count(),
    }
    
    return jsonify(data)

@app.route('/api/stream/<int:stream_id>')
def api_stream_detail(stream_id):
    """API для получения информации о стриме"""
    stream = TwitchStream.query.get_or_404(stream_id)
    
    data = {
        'id': stream.id,
        'title': stream.title,
        'description': stream.description,
        'channel': stream.channel_name,
        'date': stream.stream_date.isoformat(),
        'duration': stream.duration_formatted,
        'messages_count': stream.chat_message_count,
        'video_path': stream.local_video_path,
        'thumbnail': stream.thumbnail_url,
    }
    
    return jsonify(data)

@app.route('/api/stream/<int:stream_id>/chat')
def api_stream_chat(stream_id):
    """API для получения чата стрима"""
    stream = TwitchStream.query.get_or_404(stream_id)
    
    messages = ChatMessage.query\
        .filter_by(stream_id=stream_id)\
        .order_by(ChatMessage.message_time_seconds.asc())\
        .all()
    
    data = {
        'stream_id': stream_id,
        'messages': [m.to_dict() for m in messages],
        'total_messages': len(messages),
        'chat_is_synthetic': stream.chat_is_synthetic,
    }
    
    return jsonify(data)

@app.route('/search')
def search():
    """Поиск по стримам"""
    query = request.args.get('q', '')
    
    if query:
        results = TwitchStream.query.filter(
            TwitchStream.title.ilike(f'%{query}%'),
            TwitchStream.is_downloaded == True
        ).order_by(desc(TwitchStream.stream_date)).all()
    else:
        results = []
    
    return render_template('search.html', results=results, query=query)

@app.route('/admin/stats')
def admin_stats():
    """Статистика архива"""
    total_videos = TwitchStream.query.filter_by(is_downloaded=True).count()
    total_messages = db.session.query(ChatMessage).count()
    
    # Суммируем размер файлов
    import os
    total_size_bytes = 0
    for stream in TwitchStream.query.filter_by(is_downloaded=True).all():
        if stream.local_video_path and os.path.exists(stream.local_video_path):
            total_size_bytes += os.path.getsize(stream.local_video_path)
    
    total_size_gb = total_size_bytes / (1024**3)
    
    # Суммируем длительность
    total_duration_seconds = db.session.query(
        db.func.sum(TwitchStream.duration_seconds)
    ).filter(TwitchStream.is_downloaded == True).scalar() or 0
    
    total_duration_hours = total_duration_seconds / 3600
    
    stats = {
        'total_videos': total_videos,
        'total_messages': total_messages,
        'total_size_gb': round(total_size_gb, 2),
        'total_duration_hours': round(total_duration_hours, 1),
        'channel': TWITCH_CHANNEL,
    }
    
    return jsonify(stats)

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
