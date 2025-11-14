from setuptools import setup, find_packages

setup(
    name='goodoq-archive',
    version='1.0.0',
    description='Twitch Stream Archive with Chat Recovery',
    author='Your Name',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'Flask==2.3.3',
        'Flask-SQLAlchemy==3.0.5',
        'Flask-CORS==4.0.0',
        'yt-dlp==2023.10.13',
        'requests==2.31.0',
        'schedule==1.2.0',
        'SQLAlchemy==2.0.20',
        'python-dotenv==1.0.0',
        'click==8.1.7',
    ],
    entry_points={
        'console_scripts': [
            'goodoq-archive=run:cli',
        ],
    },
)
