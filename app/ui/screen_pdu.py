from PyQt6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from app.collectors.pdu_status import SERVER_COUNT, read_pdu_status
from app.ui.base_screen import PollingScreen


class SummaryRow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)

        self._labels = {}
        fields = [
            ("server_power_kw", "서버 전원 합계 (kW)"),
            ("tank_cdu_power_kw", "TANK+CDU 사용전력 (kW)"),
            ("total_power_kw", "전체 사용 전력 (kW)"),
        ]
        for col, (key, caption) in enumerate(fields):
            layout.addWidget(QLabel(caption), 0, col)
            value_label = QLabel("--")
            value_label.setObjectName("valueLabel")
            layout.addWidget(value_label, 1, col)
            self._labels[key] = value_label

    def update_summary(self, data: dict):
        for key, label in self._labels.items():
            value = data.get(key)
            label.setText(f"{value}" if value is not None else "--")


class ServerTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)

        headers = ["서버", "PDU 연결", "할당 전력 (kW)", "전류 (A)"]
        for col, text in enumerate(headers):
            header = QLabel(text)
            header.setObjectName("cardTitle")
            layout.addWidget(header, 0, col)

        self._rows = []
        for row in range(1, SERVER_COUNT + 1):
            name_label = QLabel("--")
            conn_label = QLabel("--")
            conn_label.setObjectName("valueLabel")
            power_label = QLabel("--")
            power_label.setObjectName("valueLabel")
            current_label = QLabel("--")
            current_label.setObjectName("valueLabel")

            layout.addWidget(name_label, row, 0)
            layout.addWidget(conn_label, row, 1)
            layout.addWidget(power_label, row, 2)
            layout.addWidget(current_label, row, 3)

            self._rows.append(
                {"name": name_label, "conn": conn_label, "power": power_label, "current": current_label}
            )

    def update_servers(self, servers: list[dict]):
        for row_widgets, server in zip(self._rows, servers):
            row_widgets["name"].setText(server.get("name", "--"))
            connected = server.get("connected")
            pdu = server.get("pdu", "--")
            row_widgets["conn"].setText(f"{pdu} 연결됨" if connected else "연결 안됨")
            row_widgets["conn"].setObjectName("valueLabel" if connected else "warningLabel")
            row_widgets["conn"].style().unpolish(row_widgets["conn"])
            row_widgets["conn"].style().polish(row_widgets["conn"])
            row_widgets["power"].setText(f"{server.get('power_kw', '--')}")
            row_widgets["current"].setText(f"{server.get('current_a', '--')}")


class PduScreen(PollingScreen):
    """PDU 버튼: 전력 사용 합계 + 서버별 PDU 연결/전력/전류."""

    def __init__(self, parent=None):
        super().__init__(read_pdu_status, parent)

        layout = QVBoxLayout(self)
        title = QLabel("PDU")
        title.setObjectName("screenTitle")
        layout.addWidget(title)

        self._summary = SummaryRow()
        layout.addWidget(self._summary)

        self._table = ServerTable()
        layout.addWidget(self._table)

        self._status = QLabel("연결 확인 중...")
        layout.addWidget(self._status)

    def update_data(self, data: dict):
        if not data.get("connected"):
            self._status.setText("PDU/서버 전력 조회 안됨")
            return
        self._status.setText("정상")
        self._summary.update_summary(data)
        self._table.update_servers(data.get("servers", []))
