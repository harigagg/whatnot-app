import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI', 'postgresql://user:password@localhost:5432/flask_db')
    SQLALCHEMY_DATABASE_URI = "postgresql://user:password@db:5432/flask_db"
    REDIS_URL = "redis://redis:6379/0"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

