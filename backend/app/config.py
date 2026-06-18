from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ai-platform"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_cors_origins: str = "http://localhost:5173"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "ai_platform"
    postgres_user: str = "postgres"
    postgres_password: str = "changeme"
    postgres_pool_size: int = 10

    doris_host: str = "localhost"
    doris_port: int = 9030
    doris_db: str = "ai_platform_olap"
    doris_user: str = "root"
    doris_password: str = ""

    storage_backend: str = "local"
    storage_root: str = "E:/pythonas/plat/storage"
    max_upload_size_mb: int = 500

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def doris_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.doris_user}:{self.doris_password}"
            f"@{self.doris_host}:{self.doris_port}/{self.doris_db}"
        )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.app_cors_origins.split(",")]

    @property
    def storage_path(self) -> Path:
        return Path(self.storage_root)

    model_config = {
        "env_file": Path(__file__).resolve().parent.parent / ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
