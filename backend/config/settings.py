from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Nova Chat Backend"
    debug: bool = True
    allowed_origins: list[str] = ["*"]
    rules_path: str = "config/rules.json"
    # API Keys
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    mistral_api_key: str | None = None
    gemini_api_key: str | None = None

    # Provider selection: "openai" | "anthropic" | "mistral"
    default_llm_provider: str = "mistral"

    # Model names per provider
    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-sonnet-4-5"
    mistral_model: str = "mistral-large-latest"
    gemini_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()