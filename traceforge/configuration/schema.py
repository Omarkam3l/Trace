"""Configuration schemas for TraceForge platform."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from traceforge.security.config import DEFAULT_JWT_SECRET, SecurityConfig, validate_jwt_secret_value


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
    """Security configuration schema.

    Mirrors traceforge.security.config.SecurityConfig's fields (plus
    `enabled`, which controls whether the auth middleware is attached to the
    gateway at all). The default and validation rules are imported from that
    module rather than redefined here, so the two configs can't drift apart
    the way they previously did.
    """

    model_config = ConfigDict(frozen=True, validate_default=True)

    enabled: bool = True
    jwt_secret: str = DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    token_expiration_minutes: int = 60
    enable_api_keys: bool = True
    rate_limit_requests: int = 100

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        return validate_jwt_secret_value(v)

    def to_security_config(self) -> SecurityConfig:
        """Convert to the SecurityConfig used by AuthProvider/JwtProvider."""
        return SecurityConfig(
            jwt_secret=self.jwt_secret,
            jwt_algorithm=self.jwt_algorithm,
            token_expiration_minutes=self.token_expiration_minutes,
            enable_api_keys=self.enable_api_keys,
            rate_limit_requests=self.rate_limit_requests,
        )


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
