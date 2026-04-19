import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///happyrobot.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY = os.getenv('API_KEY', 'cdc33e44d693a3a58451898d4ec9df862c65b954')
    FMCSA_KEY = os.getenv('FMCSA_KEY', 'cdc33e44d693a3a58451898d4ec9df862c65b954')