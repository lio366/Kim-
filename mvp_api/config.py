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
    kill_switch_enabled = os.getenv("KILL_SWITCH_ENABLED", "false").lower() == "true"
    max_budget_per_day = float(os.getenv("MAX_BUDGET_PER_DAY", "25.0"))
    cost_per_1k_chars = float(os.getenv("COST_PER_1K_CHARS", "0.02"))
    global_circuit_error_threshold = int(os.getenv("GLOBAL_CIRCUIT_ERROR_THRESHOLD", "10"))
    global_circuit_window_seconds = int(os.getenv("GLOBAL_CIRCUIT_WINDOW_SECONDS", "60"))
    global_circuit_cooldown_seconds = int(os.getenv("GLOBAL_CIRCUIT_COOLDOWN_SECONDS", "30"))


settings = Settings()
