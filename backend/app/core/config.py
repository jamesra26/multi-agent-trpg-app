from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_PROJECT_ROOT = _BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    deepseek_api_key: str = ""
    database_url: str = f"sqlite:///{(_BACKEND_DIR / 'data' / 'trpg.db').as_posix()}"
    chroma_path: str = str(_BACKEND_DIR / "data" / "chroma")
    mods_dir: str = str(_PROJECT_ROOT / "mods")

    app_version: str = "0.1.0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
