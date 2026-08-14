import logging
import random

from app.config import settings

logger = logging.getLogger(__name__)

SERVER_COUNT = 6
# 서버 i(0-based)가 붙어 있는 PDU 이름. 서버 6대 / PDU 3대 → 2대씩 배분.
SERVER_PDU_MAP = [f"PDU-{i // 2 + 1}" for i in range(SERVER_COUNT)]


async def read_pdu_status() -> dict:
    """PDU 화면: 서버/TANK+CDU/전체 사용 전력 합계 + 서버별 PDU 연결 상태."""
    if settings.MOCK_MODE:
        servers = []
        for i in range(SERVER_COUNT):
            power_kw = round(random.uniform(0.3, 0.55), 2)
            current_a = round(power_kw * 1000 / 208, 2)
            servers.append(
                {
                    "name": f"서버 {i + 1}",
                    "pdu": SERVER_PDU_MAP[i],
                    "connected": True,
                    "power_kw": power_kw,
                    "current_a": current_a,
                }
            )

        server_power_kw = round(sum(s["power_kw"] for s in servers), 2)
        tank_cdu_power_kw = round(random.uniform(3.0, 5.0), 2)
        total_power_kw = round(server_power_kw + tank_cdu_power_kw, 2)

        return {
            "connected": True,
            "server_power_kw": server_power_kw,
            "tank_cdu_power_kw": tank_cdu_power_kw,
            "total_power_kw": total_power_kw,
            "servers": servers,
        }

    # TODO: 실제 PDU/서버 전력 미터링 방식(SNMP OID 또는 서버별 BMC PowerConsumedWatts)으로 교체
    logger.warning("실제 PDU 서버 전력 조회는 아직 구현되지 않음")
    return {"connected": False, "servers": []}
