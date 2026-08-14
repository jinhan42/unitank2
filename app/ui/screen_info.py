from PyQt6.QtWidgets import QGridLayout, QLabel, QWidget

TANK_SPEC = [
    ("모델명", "UniTank IT-2400"),
    ("외형 치수", "2400 × 900 × 1100 mm (W×D×H)"),
    ("냉각유 용량", "350 L"),
    ("냉각유 종류", "제우수 S6000"),
    ("서버 수용", "2U 서버 6대"),
    ("정격 입력 전압", "208~240 VAC, 단상"),
    ("정격 냉각 용량", "30 kW"),
    ("PDU 구성", "3 × PDU (상당 20kW)"),
    ("펌프 사양", "순환 펌프 1대"),
    ("열교환기", "판형 열교환기 1대, 냉각수-냉각유 방식"),
    ("설치 위치", "전산실"),
]


class InfoScreen(QWidget):
    """INFO 버튼: 탱크 제원(스펙) 정보. 고정값이라 폴링 없이 정적으로 표시."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout(self)
        title = QLabel("탱크 제원")
        title.setObjectName("screenTitle")
        layout.addWidget(title, 0, 0, 1, 2)

        for row, (caption, value) in enumerate(TANK_SPEC, start=1):
            layout.addWidget(QLabel(caption), row, 0)
            value_label = QLabel(value)
            value_label.setObjectName("valueLabel")
            layout.addWidget(value_label, row, 1)
