"""Configuration schemas for TraceForge platform."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ServerConfig(BaseModel):
    """HTTP Server configuration."""

    model_config = ConfigDict(frozen=True)

    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False
    workers: int = 1


class StorageConfig(BaseModel):
    """Storage configuration."""

    model_config = ConfigDict(frozen=True)

    driver: str = "sqlite"
    database_uri: str = "traceforge.db"
    pool_size: int = 5


class SecurityConfigSchema(BaseModel):
    """Security configuration schema."""

    model_config = ConfigDict(frozen=True)

    enabled: bool = True
    jwt_secret: str = "traceforge-production-secret-key-change-me"
    jwt_algorithm: str = "HS256"
    token_expiration_minutes: int = 60
    enable_api_keys: bool = True
    rate_limit_requests: int = 100


class ExportConfigSchema(BaseModel):
    """Export configuration schema."""

    model_config = ConfigDict(frozen=True)

    default_format: str = "json"
    output_dir: str = "exports"


class TraceForgeConfig(BaseModel):
    """Master immutable application configuration."""

    model_config = ConfigDict(frozen=True)

    env: str = "development"
    project_name: str = "traceforge_app"
    data_dir: str = "traces"
    logs_dir: str = "logs"
    plugins_dir: str = "plugins"
    server: ServerConfig = Field(default_factory=ServerConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    security: SecurityConfigSchema = Field(default_factory=SecurityConfigSchema)
    export: ExportConfigSchema = Field(default_factory=ExportConfigSchema)
