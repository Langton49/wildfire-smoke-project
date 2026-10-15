from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    epa_key: str
    raw_data: str
    base_url: str
    epa_user: str
    model_config = SettingsConfigDict(env_file=".env.local")

settings = Settings()