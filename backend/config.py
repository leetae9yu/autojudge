from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the backend directory and project root
BACKEND_DIR = Path(__file__).parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    app_name: str = "AutoJudge API"
    debug: bool = False
    frontend_origin: str = "*"
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4.1"
    law_api_key: str = ""
    database_path: Path = PROJECT_ROOT / "data"
    port: int = 8000
    host: str = "0.0.0.0"

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
