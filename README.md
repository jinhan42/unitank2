# UniTank #2

라즈베리파이 5 + 터치스크린 디스플레이 + 외부 물리 버튼 5개(PWR/RST/TANK/PDU/INFO)로 구성된
이머젼탱크 로컬 키오스크 모니터링/제어 프로그램.

기존 loveworm(UniTank 웹 모니터링 시스템)과는 별개의 독립 프로젝트로,
원격 웹 대시보드가 아닌 **탱크에 부착된 화면에서 직접 보고 조작**하는 것이 목적.

## 버튼 구성

순서(왼쪽부터): **PWR / RST / TANK / PDU / INFO**

| 버튼 | 동작 |
|---|---|
| **PWR** | 화면 전환 — 전원 제어 화면. PDU-1/2/3 개별 ON/OFF, CMC(라즈베리파이) OFF(=shutdown) 버튼 제공. CMC ON은 소프트웨어로 불가능해 비활성화 |
| **RST** | 화면 전환 — 탱크 내부 서버(BMC) 상태 + 냉각유 흐름 상태 |
| **TANK** | 화면 전환 — 탱크 온도/유량 등 물리 센서 값 |
| **PDU** | 화면 전환 — 전력 사용 현황. 상단: 서버 전원 합계/TANK+CDU 사용전력/전체 사용 전력(kW). 하단: 서버 6대(탱크 제원 기준)별 PDU 연결 상태·할당 전력(kW)·전류(A) |
| **INFO** | 화면 전환 — 탱크 제원(모델명/치수/냉각유 용량 등 고정 스펙 정보) |

터치스크린이므로 화면 하단 네비게이션 바를 터치해도 동일하게 동작한다 (물리 버튼과 병용).

## 기술 스택

- **GUI**: PyQt6 (풀스크린 키오스크), 화면 전환은 `QStackedWidget`
- **버튼 입력**: `gpiozero` (Pi 5는 `lgpio` 백엔드 필요) — GPIO 콜백은 Qt 시그널로 변환해 메인 스레드로 전달
- **장비 통신**: `pymodbus`(탱크 센서/냉각유), `httpx`+Redfish(BMC), `pysnmp`(PDU)
- **비동기 폴링**: 네트워크 I/O가 UI를 막지 않도록 `QThread` 기반 `AsyncWorker`로 백그라운드 실행

## 프로젝트 구조

```
app/
├── main.py              # 진입점, 풀스크린 QApplication
├── config.py             # 설정 (.env로 오버라이드, GPIO 핀맵/장비 IP 등)
├── gpio_buttons.py        # 물리 버튼 → Qt 시그널
├── pdu_control.py          # PDU 개별 ON/OFF + CMC(Pi) shutdown 함수
├── collectors/              # 장비별 데이터 수집 (async)
│   ├── tank_sensor.py       #   TANK
│   ├── server_status.py     #   RST
│   └── pdu_status.py        #   PDU
└── ui/
    ├── main_window.py        # 네비게이션 바 + 화면 스택 + GPIO 연결
    ├── base_screen.py        # 주기 폴링 화면 베이스 클래스 (TANK/RST/PDU)
    ├── async_worker.py       # QThread 기반 async 실행기 (조회용)
    ├── action_worker.py       # QThread 기반 동기 액션 실행기 (제어용)
    ├── screen_pwr.py           # PWR: PDU/CMC 개별 ON/OFF 제어
    ├── screen_info.py         # INFO: 탱크 제원 (정적 데이터, 폴링 없음)
    └── screen_*.py            # 그 외 화면별 위젯
```

## 개발 (하드웨어 없이 PC에서 실행)

`.env`가 없으면 `MOCK_MODE=True`가 기본값이라 GPIO/실제 장비 없이도 창 모드로 뜬다
(랜덤 더미 데이터 표시, 물리 버튼 대신 화면 하단 버튼으로 네비게이션 테스트).

```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python -m app.main
```

## 라즈베리파이 배포

```bash
git clone https://github.com/jinhan42/unitank2.git /home/uniwide/unitank2
cd /home/uniwide/unitank2
bash scripts/install.sh
```

`install.sh`가 하는 일:
1. 시스템 패키지(Qt 런타임 의존성) 설치
2. `venv` 생성 + `requirements.txt` 설치
3. `.env` 생성 (GPIO 핀/장비 IP는 실제 배선 확정 후 값 수정 필요)
4. CMC OFF(라즈베리파이 shutdown)용 `sudo shutdown` 권한(sudoers) 등록
5. `unitank2.service` systemd 서비스 등록 (부팅 시 자동 실행)

## 확정 전 TODO (하드웨어 확보 후 채워야 함)

- [ ] 버튼 5개의 실제 GPIO 핀 번호 확정 → `.env`의 `BUTTON_PIN_*` 수정
- [ ] 탱크 센서 Modbus 레지스터 주소 → `app/collectors/tank_sensor.py`
- [ ] 냉각유 흐름 센서 Modbus 레지스터 주소 → `app/collectors/server_status.py`
- [ ] PDU 벤더 SNMP OID(전압/전류/전력, 아웃렛 제어) → `app/collectors/pdu_status.py`, `app/pdu_control.py`
- [ ] 데스크톱 환경(X11 vs Wayland/labwc) 확인 후 `unitank2.service`의 `WAYLAND_DISPLAY`/`XDG_RUNTIME_DIR` 조정
