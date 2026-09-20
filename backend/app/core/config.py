"""应用配置：统一从环境变量 / .env 读取，避免在代码里散落魔法值。"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """运行时配置，字段名即环境变量名（大小写不敏感）。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "水库日常巡查记录系统"
    api_prefix: str = "/api/v1"
    debug: bool = False

    database_url: str = "sqlite+pysqlite:///./data/reservoir.db"
    sql_echo: bool = False

    cors_origins: str = "*"

    seed_demo_data: bool = True
    default_page_size: int = 20
    max_page_size: int = 100

    @property
    def cors_origin_list(self) -> list[str]:
        """把逗号分隔的配置解析成列表，* 表示放开全部来源。"""
        raw = self.cors_origins.strip()
        if not raw or raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

