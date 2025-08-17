from pathlib import Path
import logging
from typing import Dict
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent


class Config(BaseSettings):
  SMTP_HOST: str = 'smtp.yandex.ru'
  SMTP_PORT: int = 465
  SMTP_USER: str = 'team.terrasite@yandex.ru'
  SMTP_PASSWORD: str = 'lncsiaezbmfjaltp'
  FROM_EMAIL: str = 'team.terrasite@yandex.ru'
  TO_EMAIL: str = 'team.terrasite@yandex.ru'
  LEADS_FILE: str = str(BASE_DIR / "data" / "leads.json")
  LOG_FILE: str = str(BASE_DIR / "data" / "app.log")

  class Config:
    env_prefix = 'APP_'


config = Config()

(BASE_DIR / "data").mkdir(exist_ok=True)

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s',
  handlers=[
    logging.FileHandler(config.LOG_FILE),
    logging.StreamHandler()
  ]
)
