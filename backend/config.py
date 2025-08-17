from pathlib import Path
import logging
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, EmailStr

BASE_DIR: Path = Path(__file__).parent


class Settings(BaseSettings):
    SMTP_HOST: str = Field(default='smtp.yandex.ru', description="SMTP server host")
    SMTP_PORT: int = Field(default=465, description="SMTP server port")
    SMTP_USER: str = Field(default='team.terrasite@yandex.ru', description="SMTP auth username")
    SMTP_PASSWORD: str = Field(default='lncsiaezbmfjaltp', description="SMTP auth password")
    FROM_EMAIL: EmailStr = Field(default='team.terrasite@yandex.ru', description="Sender email address")
    TO_EMAIL: EmailStr = Field(default='team.terrasite@yandex.ru', description="Recipient email address")
    LEADS_FILE: Path = Field(default=BASE_DIR / "data" / "leads.json", description="Path to leads JSON file")
    LOG_FILE: Path = Field(default=BASE_DIR / "data" / "app.log", description="Path to log file")

    class Config:
        env_prefix: str = 'APP_'
        case_sensitive: bool = False
        env_file: Optional[str] = '.env'
        env_file_encoding: str = 'utf-8'


config: Settings = Settings()

(BASE_DIR / "data").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(config.LOG_FILE)),
        logging.StreamHandler()
    ]
)