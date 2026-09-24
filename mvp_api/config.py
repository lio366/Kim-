import os


class Settings:
    jwt_secret = os.getenv("JWT_SECRET", "change-me")
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_exp_minutes = int(os.getenv("JWT_EXP_MINUTES", "60"))

    database_url = os.getenv("DATABASE_URL", "sqlite:///./kimi_mvp.db")
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

    celery_broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    celery_result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

    rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
    default_daily_quota = int(os.getenv("DEFAULT_DAILY_QUOTA", "5000"))

    primary_timeout_ms = int(os.getenv("PRIMARY_TIMEOUT_MS", "800"))
    primary_latency_ms = int(os.getenv("PRIMARY_LATENCY_MS", "120"))
    backup_latency_ms = int(os.getenv("BACKUP_LATENCY_MS", "220"))
    force_primary_failure = os.getenv("FORCE_PRIMARY_FAILURE", "false").lower() == "true"


settings = Settings()
