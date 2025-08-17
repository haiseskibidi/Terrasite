import pytest
from backend.config import Config
from pydantic import ValidationError

def test_config_defaults():
    cfg = Config()
    assert cfg.SMTP_HOST == 'smtp.yandex.ru'
    assert cfg.SMTP_PORT == 465
    assert cfg.SMTP_USER == 'team.terrasite@yandex.ru'
    assert cfg.SMTP_PASSWORD == 'lncsiaezbmfjaltp'
    assert cfg.FROM_EMAIL == 'team.terrasite@yandex.ru'
    assert cfg.TO_EMAIL == 'team.terrasite@yandex.ru'
    assert cfg.LEADS_FILE == 'leads.json'

def test_config_with_env(monkeypatch):
    monkeypatch.setenv("APP_SMTP_HOST", "test.host")
    monkeypatch.setenv("APP_SMTP_PORT", "587")
    cfg = Config()
    assert cfg.SMTP_HOST == "test.host"
    assert cfg.SMTP_PORT == 587

def test_config_validation_error(monkeypatch):
    monkeypatch.setenv("APP_SMTP_PORT", "invalid")
    with pytest.raises(ValidationError):
        Config()