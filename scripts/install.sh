#!/bin/bash
# UniTank #2 (라즈베리파이5 + 터치스크린 + 물리버튼 5개) 설치 스크립트
# Raspberry Pi OS (Debian 기반, 64-bit) 전용

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CURRENT_USER="${SUDO_USER:-$(whoami)}"

echo "======================================================"
echo "  UniTank #2 설치"
echo "  프로젝트 경로: $PROJECT_DIR"
echo "  실행 사용자:   $CURRENT_USER"
echo "======================================================"

echo ""
echo "[1/4] 시스템 패키지 설치..."
sudo apt-get update -q
sudo apt-get install -y python3-pip python3-venv git \
  libgl1 libegl1 libxkbcommon0 libxcb-cursor0

echo ""
echo "[2/4] Python 가상환경 및 패키지 설치..."
python3 -m venv "$PROJECT_DIR/venv"
"$PROJECT_DIR/venv/bin/pip" install -q --upgrade pip
"$PROJECT_DIR/venv/bin/pip" install -q -r "$PROJECT_DIR/requirements.txt"

echo ""
echo "[3/4] .env 파일 생성 (없을 경우만)..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
  cat > "$PROJECT_DIR/.env" << 'ENVEOF'
MOCK_MODE=false

BUTTON_PIN_PWR=5
BUTTON_PIN_RST=6
BUTTON_PIN_TANK=13
BUTTON_PIN_PDU=19
BUTTON_PIN_INFO=26

TANK_MODBUS_HOST=192.168.1.3
SERVER_BMC_HOST=192.168.1.100
COOLANT_MODBUS_HOST=192.168.1.3
PDU_HOST=192.168.1.210
ENVEOF
  echo "      .env 생성됨 (실제 배선/장비 IP에 맞게 수정 필요)"
else
  echo "      .env 이미 존재 (유지)"
fi

# PWR 버튼의 Pi 자체 종료 기능에 필요한 sudo 권한
SUDOERS_FILE="/etc/sudoers.d/unitank2"
if [ ! -f "$SUDOERS_FILE" ]; then
  echo "$CURRENT_USER ALL=(ALL) NOPASSWD: /sbin/shutdown" | sudo tee "$SUDOERS_FILE" > /dev/null
  sudo chmod 440 "$SUDOERS_FILE"
fi

echo ""
echo "[4/4] systemd 서비스 등록..."
sudo tee /etc/systemd/system/unitank2.service > /dev/null << SVCEOF
[Unit]
Description=UniTank 2 Kiosk App
After=graphical.target
Wants=graphical.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
# 데스크톱 환경이 X11/Wayland(labwc) 중 무엇인지에 따라 아래 값을 맞춰야 함
# (loveworm 프로젝트에서도 kanshi 재실행 시 WAYLAND_DISPLAY/XDG_RUNTIME_DIR 지정 필요했음)
Environment=WAYLAND_DISPLAY=wayland-0
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=PYTHONPATH=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python3 -m app.main
Restart=always
RestartSec=5

[Install]
WantedBy=graphical.target
SVCEOF

sudo systemctl daemon-reload
sudo systemctl enable unitank2

echo ""
echo "======================================================"
echo "  설치 완료! 재부팅 후 자동 실행됩니다."
echo "  수동 실행 확인: sudo systemctl start unitank2"
echo "======================================================"
