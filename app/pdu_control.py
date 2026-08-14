import asyncio
import logging
import subprocess

from app.config import settings

logger = logging.getLogger(__name__)


async def _snmp_set_outlet(outlet: int, on: bool) -> bool:
    """SNMP SET으로 PDU 아웃렛 전원을 제어한다.

    OID는 PDU 벤더마다 다르므로, 실제 장비 스펙 확보 후 OID를 채워 넣어야 한다.
    지금은 통신 골격만 구성해둔다.
    """
    from pysnmp.hlapi.v3arch.asyncio import (
        CommunityData,
        ContextData,
        ObjectIdentity,
        ObjectType,
        SnmpEngine,
        UdpTransportTarget,
        set_cmd,
    )

    # TODO: 실제 PDU 벤더의 outlet-control OID로 교체
    outlet_oid = f"1.3.6.1.4.1.0.0.0.{outlet}"
    value = 1 if on else 0

    error_indication, error_status, _, _ = await set_cmd(
        SnmpEngine(),
        CommunityData(settings.PDU_SNMP_COMMUNITY),
        await UdpTransportTarget.create((settings.PDU_HOST, settings.PDU_SNMP_PORT)),
        ContextData(),
        ObjectType(ObjectIdentity(outlet_oid), value),
    )

    if error_indication or error_status:
        logger.error("PDU SNMP 제어 실패: %s / %s", error_indication, error_status)
        return False
    return True


def shutdown_pdu_outlet(outlet: int | None = None) -> bool:
    """PWR 버튼: 외부 장비 전원(PDU 아웃렛)을 차단한다."""
    outlet = outlet or settings.PDU_OUTLET_INDEX

    if settings.MOCK_MODE:
        logger.info("[MOCK] PDU 아웃렛 %s OFF", outlet)
        return True

    try:
        return asyncio.run(_snmp_set_outlet(outlet, on=False))
    except Exception:
        logger.exception("PDU 전원 차단 중 오류")
        return False


def shutdown_raspberry_pi() -> None:
    """PWR 버튼: 라즈베리파이 자체 전원을 종료한다.

    sudoers에 NOPASSWD로 `/sbin/shutdown` 권한이 등록되어 있어야 한다.
    (scripts/install.sh 참고)
    """
    if settings.MOCK_MODE:
        logger.info("[MOCK] Raspberry Pi shutdown 호출됨 (실제 종료하지 않음)")
        return

    subprocess.run(["sudo", "/sbin/shutdown", "-h", "now"], check=False)
