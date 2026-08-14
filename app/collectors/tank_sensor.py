import logging
import random

from app.config import settings

logger = logging.getLogger(__name__)


async def read_tank_sensors() -> dict:
    """TANK 화면: 탱크 온도/유량 등 물리 센서 값.

    레지스터 맵은 실제 장비 스펙 확보 후 채워 넣는다.
    """
    if settings.MOCK_MODE:
        return {
            "temp_upper": round(random.uniform(35, 45), 1),
            "temp_lower": round(random.uniform(35, 45), 1),
            "flow_upper": round(random.uniform(5, 15), 2),
            "flow_lower": round(random.uniform(5, 15), 2),
            "connected": True,
        }

    from pymodbus.client import AsyncModbusTcpClient

    client = AsyncModbusTcpClient(settings.TANK_MODBUS_HOST, port=settings.TANK_MODBUS_PORT)
    try:
        await client.connect()
        if not client.connected:
            return {"connected": False}

        # TODO: 실제 레지스터 주소로 교체
        result = await client.read_holding_registers(address=0, count=4)
        if result.isError():
            return {"connected": False}

        regs = result.registers
        return {
            "temp_upper": regs[0] / 10,
            "temp_lower": regs[1] / 10,
            "flow_upper": regs[2] / 10,
            "flow_lower": regs[3] / 10,
            "connected": True,
        }
    except Exception:
        logger.exception("탱크 센서 읽기 오류")
        return {"connected": False}
    finally:
        client.close()
