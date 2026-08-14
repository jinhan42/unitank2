from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # 개발용: 실제 GPIO/장비가 없는 PC에서도 UI를 띄워볼 수 있게 하는 스위치
    MOCK_MODE: bool = True

    # --- 버튼 GPIO 핀 매핑 (BCM 번호) ---
    # 하드웨어 배선 확정 전까지의 placeholder. 실제 배선 후 .env 로 덮어쓸 것.
    BUTTON_PIN_PWR: int = 5
    BUTTON_PIN_RST: int = 6
    BUTTON_PIN_TANK: int = 13
    BUTTON_PIN_PDU: int = 19
    BUTTON_PIN_INFO: int = 26
    BUTTON_BOUNCE_TIME: float = 0.05  # 디바운스 (초)

    # --- 탱크 센서 (Modbus TCP) ---
    TANK_MODBUS_HOST: str = "192.168.1.3"
    TANK_MODBUS_PORT: int = 502

    # --- 탱크 내부 서버 BMC (Redfish) ---
    SERVER_BMC_HOST: str = "192.168.1.100"
    SERVER_BMC_USERNAME: str = "admin"
    SERVER_BMC_PASSWORD: str = "admin"

    # --- 냉각유 흐름 (Modbus TCP, RST 화면에서 서버 상태와 함께 표시) ---
    COOLANT_MODBUS_HOST: str = "192.168.1.3"
    COOLANT_MODBUS_PORT: int = 502

    # --- PDU (SNMP) ---
    PDU_HOST: str = "192.168.1.210"
    PDU_SNMP_COMMUNITY: str = "public"
    PDU_SNMP_PORT: int = 161
    PDU_OUTLET_INDEX: int = 1  # PWR 버튼이 차단할 아웃렛 번호

    DATA_POLL_INTERVAL_SEC: int = 5


settings = Settings()
