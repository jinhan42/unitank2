import logging
import random

from app.config import settings

logger = logging.getLogger(__name__)


async def read_pdu_status() -> dict:
    """PDU 화면: PDU 전력 상태."""
    if settings.MOCK_MODE:
        return {
            "voltage": round(random.uniform(210, 230), 1),
            "current": round(random.uniform(1, 8), 2),
            "power_w": round(random.uniform(300, 1200), 1),
            "connected": True,
        }

    from pysnmp.hlapi.v3arch.asyncio import (
        CommunityData,
        ContextData,
        ObjectIdentity,
        ObjectType,
        SnmpEngine,
        UdpTransportTarget,
        get_cmd,
    )

    # TODO: 실제 PDU 벤더의 전압/전류/전력 OID로 교체
    oids = {
        "voltage": "1.3.6.1.4.1.0.0.1.0",
        "current": "1.3.6.1.4.1.0.0.2.0",
        "power_w": "1.3.6.1.4.1.0.0.3.0",
    }

    result = {}
    try:
        target = await UdpTransportTarget.create((settings.PDU_HOST, settings.PDU_SNMP_PORT))
        for key, oid in oids.items():
            error_indication, error_status, _, var_binds = await get_cmd(
                SnmpEngine(),
                CommunityData(settings.PDU_SNMP_COMMUNITY),
                target,
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
            )
            if error_indication or error_status:
                raise RuntimeError(f"{key} 조회 실패: {error_indication or error_status}")
            result[key] = float(var_binds[0][1])
        result["connected"] = True
    except Exception:
        logger.exception("PDU SNMP 조회 오류")
        result = {"connected": False}

    return result
