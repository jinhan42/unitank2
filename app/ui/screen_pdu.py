from PyQt6.QtWidgets import QGridLayout, QLabel

from app.collectors.pdu_status import read_pdu_status
from app.ui.base_screen import PollingScreen


class PduScreen(PollingScreen):
    """PDU 버튼: PDU 전력 상태."""

    def __init__(self, parent=None):
        super().__init__(read_pdu_status, parent)

        layout = QGridLayout(self)
        self._title = QLabel("PDU")
        self._title.setObjectName("screenTitle")
        layout.addWidget(self._title, 0, 0, 1, 2)

        self._labels = {}
        fields = [
            ("voltage", "전압 (V)"),
            ("current", "전류 (A)"),
            ("power_w", "전력 (W)"),
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
        self._status.setText("정상" if data.get("connected") else "PDU 연결 안됨")
        for key, label in self._labels.items():
            value = data.get(key)
            label.setText(f"{value}" if value is not None else "--")
