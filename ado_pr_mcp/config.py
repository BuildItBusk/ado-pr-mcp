"""Configuration management for Azure DevOps PR MCP server."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Required
    azure_devops_pat: str = Field(
        ...,
        description="Azure DevOps Personal Access Token (requires Code Read scope)",
    )

    # Optional defaults
    ado_organization: Optional[str] = Field(
        default=None,
        description="Default Azure DevOps organization",
    )
    ado_project: Optional[str] = Field(
        default=None,
        description="Default Azure DevOps project",
    )
    ado_repository: Optional[str] = Field(
        default=None,
        description="Default Azure DevOps repository",
    )

    # Server configuration
    mcp_transport: str = Field(
        default="stdio",
        description="MCP transport type (stdio or http)",
    )
    mcp_log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the singleton Settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
