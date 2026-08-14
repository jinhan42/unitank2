import socket

import psutil


async def read_system_info() -> dict:
    """INFO 화면: 라즈베리파이 자체 시스템 정보."""
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip_address = "-"

    cpu_temp = None
    try:
        temps = psutil.sensors_temperatures()
        if "cpu_thermal" in temps and temps["cpu_thermal"]:
            cpu_temp = temps["cpu_thermal"][0].current
    except Exception:
        pass

    uptime_sec = int(psutil.boot_time())
    disk = psutil.disk_usage("/")

    return {
        "connected": True,
        "hostname": hostname,
        "ip_address": ip_address,
        "cpu_percent": psutil.cpu_percent(interval=None),
        "cpu_temp": cpu_temp,
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": disk.percent,
        "boot_time_epoch": uptime_sec,
    }
