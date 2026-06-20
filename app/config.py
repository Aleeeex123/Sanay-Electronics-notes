import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Supah-Key'

    DB_NAME = os.environ.get('DB_NAME') or 'mywebapp_db'
    DB_USER = os.environ.get('DB_USER') or 'postgres'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or '1234'
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_PORT = os.environ.get('DB_PORT') or '5432'