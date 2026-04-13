from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "rihla"
    postgres_user: str = "rihla_user"
    postgres_password: str = "rihla_pass"

    # Ollama
    ollama_base_url: str = "http://host.docker.internal:11434"
    llm_model: str = "qwen2.5:7b"
    embed_model: str = "nomic-embed-text"

    # Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379

    # Agency
    agency_email: str = "contact.alrihla@gmail.com"
    waha_api_key: str = "rihla2026"

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    class Config:
        env_file = ".env"


settings = Settings()
