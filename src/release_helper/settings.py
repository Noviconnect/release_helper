from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SlackSettings(BaseSettings):
    bot_token: str
    deploy_channel: str
    channels: dict[str, str] = Field(default_factory=dict)


class LinearSettings(BaseSettings):
    token: str


class NotionSettings(BaseSettings):
    token: str
    parent_page_id: str


class OpenAISettings(BaseSettings):
    api_key: str
    model: str = "gpt-4o"


class HelperSettings(BaseSettings):
    deploy: bool = False
    github_token: str
    linear: LinearSettings
    slack: SlackSettings
    notion: NotionSettings = None
    openai: OpenAISettings = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
    )
    helper: HelperSettings
    github_repository: str = Field(validation_alias="GITHUB_REPOSITORY")
