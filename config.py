import logging
from typing import Dict
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    SMTP_HOST: str = 'smtp.yandex.ru'
    SMTP_PORT: int = 465
    SMTP_USER: str = 'team.terrasite@yandex.ru'
    SMTP_PASSWORD: str = 'lncsiaezbmfjaltp'
    FROM_EMAIL: str = 'team.terrasite@yandex.ru'
    TO_EMAIL: str = 'team.terrasite@yandex.ru'
    LEADS_FILE: str = 'leads.json'

    class Config:
        env_prefix = 'APP_'

config = Config()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)