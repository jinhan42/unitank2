from PyQt6.QtWidgets import QGridLayout, QLabel

from app.collectors.tank_sensor import read_tank_sensors
from app.ui.base_screen import PollingScreen


class TankScreen(PollingScreen):
    """TANK 버튼: 탱크 온도/유량 등 물리 센서 값."""

    def __init__(self, parent=None):
        super().__init__(read_tank_sensors, parent)

        layout = QGridLayout(self)
        self._title = QLabel("TANK")
        self._title.setObjectName("screenTitle")
        layout.addWidget(self._title, 0, 0, 1, 2)

        self._labels = {}
        fields = [
            ("temp_upper", "상층 온도 (℃)"),
            ("temp_lower", "하층 온도 (℃)"),
            ("flow_upper", "상부 유량 (L/min)"),
            ("flow_lower", "하부 유량 (L/min)"),
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
        if not data.get("connected"):
            self._status.setText("장비 연결 안됨")
            return
        self._status.setText("정상")
        for key, label in self._labels.items():
            value = data.get(key)
            label.setText(f"{value}" if value is not None else "--")
