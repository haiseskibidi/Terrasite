from pathlib import Path
import logging
from pydantic_settings import BaseSettings
from pydantic import Field, EmailStr, ConfigDict

BASE_DIR: Path = Path(__file__).parent


class Settings(BaseSettings):
  smtp_host: str = Field(default='smtp.yandex.ru', env='APP_SMTP_HOST', description="SMTP server host")
  smtp_port: int = Field(default=465, env='APP_SMTP_PORT', description="SMTP server port", ge=1, le=65535)
  smtp_user: str = Field(default='team.terrasite@yandex.ru', env='APP_SMTP_USER', description="SMTP auth username")
  smtp_password: str = Field(default='lncsiaezbmfjaltp', env='APP_SMTP_PASSWORD', description="SMTP auth password")
  from_email: EmailStr = Field(default='team.terrasite@yandex.ru', env='APP_FROM_EMAIL',
                               description="Sender email address")
  to_email: EmailStr = Field(default='team.terrasite@yandex.ru', env='APP_TO_EMAIL',
                             description="Recipient email address")
  leads_file: Path = Field(default=BASE_DIR / "data" / "leads.json", env='APP_LEADS_FILE',
                           description="Path to leads JSON file")
  log_file: Path = Field(default=BASE_DIR / "data" / "app.log", env='APP_LOG_FILE', description="Path to log file")

  model_config = ConfigDict(
    env_prefix='APP_',
    case_sensitive=False,
    env_file='.env',
    env_file_encoding='utf-8',
    extra='ignore'
  )


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
