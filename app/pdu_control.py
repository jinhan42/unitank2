import asyncio
import logging
import subprocess

from app.config import settings

logger = logging.getLogger(__name__)


async def _snmp_set_outlet(host: str, outlet: int, on: bool) -> bool:
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
        await UdpTransportTarget.create((host, settings.PDU_SNMP_PORT)),
        ContextData(),
        ObjectType(ObjectIdentity(outlet_oid), value),
    )

    if error_indication or error_status:
        logger.error("PDU(%s) SNMP 제어 실패: %s / %s", host, error_indication, error_status)
        return False
    return True


def set_pdu_power(pdu_index: int, on: bool) -> bool:
    """전원 제어 화면: PDU 1대의 전원을 개별적으로 ON/OFF 한다.

    pdu_index: 0=PDU-1, 1=PDU-2, 2=PDU-3 (settings.PDU_HOSTS 순서)
    """
    host = settings.PDU_HOSTS[pdu_index]
    outlet = settings.PDU_OUTLET_INDEX

    if settings.MOCK_MODE:
        logger.info("[MOCK] PDU-%s(%s) 아웃렛 %s %s", pdu_index + 1, host, outlet, "ON" if on else "OFF")
        return True

    try:
        return asyncio.run(_snmp_set_outlet(host, outlet, on))
    except Exception:
        logger.exception("PDU-%s(%s) 전원 제어 중 오류", pdu_index + 1, host)
        return False


def set_cmc_power(on: bool) -> bool:
    """전원 제어 화면: CMC(라즈베리파이 자체) 전원 제어.

    OFF는 실제 shutdown을 수행한다 (sudoers에 NOPASSWD로 `/sbin/shutdown` 권한 필요,
    scripts/install.sh 참고). ON은 소프트웨어로 종료된 Pi를 다시 켤 수 없으므로 지원하지 않는다
    (화면에서 버튼 자체를 비활성화해둔다).
    """
    if on:
        logger.warning("CMC ON은 지원되지 않음 (라즈베리파이 자체는 소프트웨어로 재기동 불가)")
        return False

    if settings.MOCK_MODE:
        logger.info("[MOCK] CMC(Raspberry Pi) shutdown 호출됨 (실제 종료하지 않음)")
        return True

    subprocess.run(["sudo", "/sbin/shutdown", "-h", "now"], check=False)
    return True
