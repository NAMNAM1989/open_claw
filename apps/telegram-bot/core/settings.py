from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_bot_token: str = ""
    allowed_chat_ids: str = ""

    supabase_url: str = ""
    supabase_service_role_key: str = ""

    ai_provider: str = "openclaw"
    openclaw_base_url: str = "http://127.0.0.1:18789/v1"
    openclaw_gateway_token: str = ""
    openclaw_agent_id: str = "default"
    openclaw_timeout: float = 90.0

    quote_engine_enabled: bool = True
    volumetric_divisor: int = 6000
    quote_min_charge_default: float = 0.0
    quote_fuel_surcharge_pct: float = 0.0
    route_aliases: str = "HCM:SGN,HAN:HAN"

    # Ops / eCargo
    ops_enabled: bool = True
    ecargo_storage_state: str = "data/ecargo_storage.json"
    ecargo_base_url: str = "https://ecargo.scsc.vn"
    ecargo_create_path: str = "/Export/VCTOrder/Create"
    ecargo_dry_run: bool = True
    ecargo_default_pcs: int = 1
    ecargo_default_gw: float = 1.0

    gmail_user: str = ""
    gmail_app_password: str = ""
    mail_watch_enabled: bool = False
    mail_watch_interval_sec: int = 60

    # Documents / vision
    image_reader_enabled: bool = True
    scale_ticket_ocr_enabled: bool = True
    openclaw_vision_timeout: float = 180.0

    # Chat / reports
    chat_enabled: bool = True

    @property
    def ecargo_create_url(self) -> str:
        base = self.ecargo_base_url.rstrip("/")
        path = self.ecargo_create_path if self.ecargo_create_path.startswith("/") else f"/{self.ecargo_create_path}"
        return f"{base}{path}"

    def ecargo_storage_path(self) -> Path | None:
        rel = (self.ecargo_storage_state or "").strip()
        if not rel:
            return None
        return Path(rel)

    def allowed_ids(self) -> set[int]:
        if not self.allowed_chat_ids.strip():
            return set()
        return {int(x.strip()) for x in self.allowed_chat_ids.split(",") if x.strip()}

    def route_alias_map(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for part in self.route_aliases.split(","):
            if ":" not in part:
                continue
            src, dst = part.split(":", 1)
            out[src.strip().upper()] = dst.strip().upper()
        return out


settings = Settings()
