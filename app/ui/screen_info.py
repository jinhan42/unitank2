from datetime import datetime

from PyQt6.QtWidgets import QGridLayout, QLabel

from app.collectors.system_info import read_system_info
from app.ui.base_screen import PollingScreen


class InfoScreen(PollingScreen):
    """INFO 버튼: 시스템(라즈베리파이) 정보."""

    def __init__(self, parent=None):
        super().__init__(read_system_info, parent)

        layout = QGridLayout(self)
        self._title = QLabel("SYSTEM INFO")
        self._title.setObjectName("screenTitle")
        layout.addWidget(self._title, 0, 0, 1, 2)

        self._labels = {}
        fields = [
            ("hostname", "호스트명"),
            ("ip_address", "IP 주소"),
            ("cpu_percent", "CPU 사용률 (%)"),
            ("cpu_temp", "CPU 온도 (℃)"),
            ("memory_percent", "메모리 사용률 (%)"),
            ("disk_percent", "디스크 사용률 (%)"),
            ("boot_time_epoch", "부팅 시각"),
        ]
        for row, (key, caption) in enumerate(fields, start=1):
            layout.addWidget(QLabel(caption), row, 0)
            value_label = QLabel("--")
            value_label.setObjectName("valueLabel")
            layout.addWidget(value_label, row, 1)
            self._labels[key] = value_label

    def update_data(self, data: dict):
        for key, label in self._labels.items():
            value = data.get(key)
            if key == "boot_time_epoch" and value:
                value = datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M")
            label.setText(f"{value}" if value is not None else "--")
