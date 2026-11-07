from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    offline_mode: bool = True
    ai_enabled: bool = True
    
    # DeepSeek / Klinch AI
    klinch_api_key: str = ""
    deepseek_model: str = "deepseek-flash"
    deepseek_base_url: str = "https://api.klinch.cloud/v1"

    telegram_api_base: str = "https://api.telegram.org"

settings = Settings()
