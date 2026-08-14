from PyQt6.QtWidgets import QGridLayout, QLabel

from app.collectors.server_status import read_server_status
from app.ui.base_screen import PollingScreen


class ServerScreen(PollingScreen):
    """RST 버튼: 탱크 내부 서버(BMC) 상태 + 냉각유 흐름 상태."""

    def __init__(self, parent=None):
        super().__init__(read_server_status, parent)

        layout = QGridLayout(self)
        self._title = QLabel("SERVER STATUS")
        self._title.setObjectName("screenTitle")
        layout.addWidget(self._title, 0, 0, 1, 2)

        self._labels = {}
        fields = [
            ("power_state", "서버 전원 상태"),
            ("cpu_temp", "CPU 온도 (℃)"),
            ("coolant_flow", "냉각유 흐름 (L/min)"),
        ]
        for row, (key, caption) in enumerate(fields, start=1):
            layout.addWidget(QLabel(caption), row, 0)
            value_label = QLabel("--")
            value_label.setObjectName("valueLabel")
            layout.addWidget(value_label, row, 1)
            self._labels[key] = value_label

        self._status = QLabel("연결 확인 중...")
        layout.addWidget(self._status, len(fields) + 1, 0, 1, 2)

    def update_data(self, data: dict):
        self._status.setText("정상" if data.get("connected") else "BMC 연결 안됨")
        for key, label in self._labels.items():
            value = data.get(key)
            label.setText(f"{value}" if value is not None else "--")
