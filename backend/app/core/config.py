from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Configuration loaded from the project-root .env file."""

    app_name: str = "ShopPilot AI API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173"
    sql_server: str = "localhost"
    sql_database: str = "ShopPilotAI"
    sql_driver: str = "ODBC Driver 18 for SQL Server"
    sql_trusted_connection: str = "yes"
    sql_trust_server_certificate: str = "yes"
    jwt_secret_key: str = "change-me-before-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    payment_test_mode: bool = True
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.1:latest"

    # Resolve from this module rather than the shell's working directory, so
    # Uvicorn reads the project .env consistently on Windows.
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def database_url(self) -> str:
        connection_string = (
            f"DRIVER={{{self.sql_driver}}};SERVER={self.sql_server};DATABASE={self.sql_database};"
            f"Trusted_Connection={self.sql_trusted_connection};TrustServerCertificate={self.sql_trust_server_certificate};"
        )
        return f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def razorpay_enabled(self) -> bool:
        return bool(self.razorpay_key_id and self.razorpay_key_secret and not self.payment_test_mode)


@lru_cache
def get_settings() -> Settings:
    return Settings()
