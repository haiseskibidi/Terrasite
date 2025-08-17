import pytest
from pydantic import ValidationError
from backend.config import Settings

def test_config_defaults():
    cfg = Settings()
    assert cfg.smtp_host == "smtp.yandex.ru"
    assert cfg.smtp_port == 465
    assert cfg.smtp_user == "team.terrasite@yandex.ru"
    assert cfg.smtp_password == "lncsiaezbmfjaltp"
    assert cfg.from_email == "team.terrasite@yandex.ru"
    assert cfg.to_email == "team.terrasite@yandex.ru"
    assert cfg.leads_file.name == "leads.json"
    assert cfg.log_file.name == "app.log"

def test_config_with_env(monkeypatch):
    monkeypatch.setenv("APP_SMTP_HOST", "test.host")
    monkeypatch.setenv("APP_SMTP_PORT", "587")
    cfg = Settings()
    assert cfg.smtp_host == "test.host"
    assert cfg.smtp_port == 587

@pytest.mark.parametrize("invalid_port", ["abc", "-1", "1000000"])
def test_config_validation_error(invalid_port, monkeypatch):
    monkeypatch.setenv("APP_SMTP_PORT", invalid_port)
    with pytest.raises(ValidationError):
        Settings()