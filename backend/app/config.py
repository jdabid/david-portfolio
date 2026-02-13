"""
Application settings loaded from environment variables.
Uses pydantic-settings to validate and type env vars at startup.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "David Portfolio API"
    debug: bool = False
    secret_key: str = "change-me"
    allowed_origins: str = "http://localhost:3000"

    # PostgreSQL
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "portfolio_db"
    postgres_user: str = "portfolio_user"
    postgres_password: str = "portfolio_pass"

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    # RabbitMQ
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "/"

    # AI / LLM
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-20250514"
    chroma_persist_dir: str = "./data/chromadb"
    knowledge_base_dir: str = "./data/knowledge"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}/{self.rabbitmq_vhost}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
