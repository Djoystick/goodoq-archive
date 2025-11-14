// ============ ИНИЦИАЛИЗАЦИЯ СТРАНИЦЫ ============

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎮 Archiver loaded');
    
    // Инициализируем функции
    loadStats();
    initSearch();
    initVideoPlayer();
});

// ============ ЗАГРУЗКА СТАТИСТИКИ ============

async function loadStats() {
    try {
        const response = await fetch('/api/streams?per_page=1');
        const data = await response.json();
        
        console.log('📊 Stats loaded:', data);
    } catch (error) {
        console.error('❌ Error loading stats:', error);
    }
}

// ============ ПОИСК ============

function initSearch() {
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const query = this.querySelector('input[name="q"]').value.trim();
            if (!query) {
                e.preventDefault();
                return false;
            }
        });
    }
}

// ============ ВИДЕОПЛЕЕР ============

function initVideoPlayer() {
    const videoPlayer = document.getElementById('video-player');
    if (!videoPlayer) return;
    
    // Обработка полноэкранного режима
    videoPlayer.addEventListener('fullscreenchange', function() {
        console.log('Fullscreen toggle');
    });
    
    // Кастомные горячие клавиши
    document.addEventListener('keydown', function(e) {
        if (e.target === videoPlayer || videoPlayer.contains(e.target)) {
            switch(e.code) {
                case 'Space':
                    e.preventDefault();
                    if (videoPlayer.paused) {
                        videoPlayer.play();
                    } else {
                        videoPlayer.pause();
                    }
                    break;
                case 'ArrowLeft':
                    videoPlayer.currentTime = Math.max(0, videoPlayer.currentTime - 5);
                    break;
                case 'ArrowRight':
                    videoPlayer.currentTime = Math.min(videoPlayer.duration, videoPlayer.currentTime + 5);
                    break;
            }
        }
    });
}

// ============ ФОРМАТИРОВАНИЕ ВРЕМЕНИ ============

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
}

// ============ API ФУНКЦИИ ============

async function fetchJSON(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        return null;
    }
}

// ============ УТИЛИТЫ ============

function escapeHTML(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============ ЭКСПОРТ ============

window.Archiver = {
    formatTime,
    fetchJSON,
    escapeHTML,
    debounce,
};
