import logging
import random

from app.config import settings

logger = logging.getLogger(__name__)


async def read_server_status() -> dict:
    """RST 화면: 탱크 내부 서버(BMC) 상태 + 냉각유 흐름 상태."""
    if settings.MOCK_MODE:
        return {
            "power_state": "On",
            "cpu_temp": round(random.uniform(40, 70), 1),
            "coolant_flow": round(random.uniform(4, 10), 2),
            "connected": True,
        }

    import httpx

    power_state = "Unknown"
    connected = False
    try:
        async with httpx.AsyncClient(verify=False, timeout=5) as client:
            resp = await client.get(
                f"https://{settings.SERVER_BMC_HOST}/redfish/v1/Systems/1",
                auth=(settings.SERVER_BMC_USERNAME, settings.SERVER_BMC_PASSWORD),
            )
            if resp.status_code == 200:
                data = resp.json()
                power_state = data.get("PowerState", "Unknown")
                connected = True
    except Exception:
        logger.exception("BMC(Redfish) 상태 조회 오류")

    coolant_flow = await _read_coolant_flow()

    return {
        "power_state": power_state,
        "coolant_flow": coolant_flow,
        "connected": connected,
    }


async def _read_coolant_flow() -> float | None:
    from pymodbus.client import AsyncModbusTcpClient

    client = AsyncModbusTcpClient(settings.COOLANT_MODBUS_HOST, port=settings.COOLANT_MODBUS_PORT)
    try:
        await client.connect()
        if not client.connected:
            return None
        # TODO: 실제 레지스터 주소로 교체
        result = await client.read_holding_registers(address=10, count=1)
        if result.isError():
            return None
        return result.registers[0] / 10
    except Exception:
        logger.exception("냉각유 흐름 읽기 오류")
        return None
    finally:
        client.close()
