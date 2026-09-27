from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    database_url: str
    # Rol app_admin (BYPASSRLS): solo lo usan los jobs de mantenimiento, nunca la API web.
    database_admin_url: str = ""
    supabase_url: str
    supabase_anon_key: str
    frontend_origin: str


settings = Settings()
