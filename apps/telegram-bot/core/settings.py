from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_bot_token: str = ""
    allowed_chat_ids: str = ""

    openclaw_base_url: str = "http://openclaw-gateway.railway.internal:18789/v1"
    openclaw_gateway_token: str = ""
    openclaw_agent_id: str = "default"
    openclaw_timeout: float = 180.0

    volumetric_divisor: float = 6000.0

    def allowed_ids(self) -> set[int]:
        if not self.allowed_chat_ids.strip():
            return set()
        return {int(x.strip()) for x in self.allowed_chat_ids.split(",") if x.strip()}


settings = Settings()
