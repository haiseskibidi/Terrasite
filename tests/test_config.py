import pytest
from backend.config import config, Settings
from pydantic import ValidationError

def test_config_defaults():
    cfg = Settings()
    assert cfg.smtp_host == 'smtp.yandex.ru'
    assert cfg.smtp_port == 465
    assert cfg.smtp_user == 'team.terrasite@yandex.ru'
    assert cfg.smtp_password == 'lncsiaezbmfjaltp'
    assert cfg.from_email == 'team.terrasite@yandex.ru'
    assert cfg.to_email == 'team.terrasite@yandex.ru'
    assert 'leads.json' in str(cfg.leads_file)

def test_config_with_env(monkeypatch):
    monkeypatch.setenv("APP_SMTP_HOST", "test.host")
    monkeypatch.setenv("APP_SMTP_PORT", "587")
    cfg = Settings()
    assert cfg.smtp_host == "test.host"
    assert cfg.smtp_port == 587

def test_config_validation_error(monkeypatch):
    monkeypatch.setenv("APP_SMTP_PORT", "invalid")
    with pytest.raises(ValidationError):
        Settings()