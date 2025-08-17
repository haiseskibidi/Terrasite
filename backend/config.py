from pathlib import Path
import logging
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, EmailStr

BASE_DIR: Path = Path(__file__).parent


class Settings(BaseSettings):
    smtp_host: str = Field(default='smtp.yandex.ru', alias='SMTP_HOST', description="SMTP server host")
    smtp_port: int = Field(default=465, alias='SMTP_PORT', description="SMTP server port")
    smtp_user: str = Field(default='team.terrasite@yandex.ru', alias='SMTP_USER', description="SMTP auth username")
    smtp_password: str = Field(default='lncsiaezbmfjaltp', alias='SMTP_PASSWORD', description="SMTP auth password")
    from_email: EmailStr = Field(default='team.terrasite@yandex.ru', alias='FROM_EMAIL', description="Sender email address")
    to_email: EmailStr = Field(default='team.terrasite@yandex.ru', alias='TO_EMAIL', description="Recipient email address")
    leads_file: Path = Field(default=BASE_DIR / "data" / "leads.json", alias='LEADS_FILE', description="Path to leads JSON file")
    log_file: Path = Field(default=BASE_DIR / "data" / "app.log", alias='LOG_FILE', description="Path to log file")

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
        logging.FileHandler(str(config.log_file)),
        logging.StreamHandler()
    ]
)