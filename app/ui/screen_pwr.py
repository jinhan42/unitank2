from PyQt6.QtWidgets import QGridLayout, QLabel, QPushButton, QWidget

from app.config import settings
from app.pdu_control import set_cmc_power, set_pdu_power
from app.ui.action_worker import ActionWorker


class PowerControlScreen(QWidget):
    """PWR 버튼: PDU 3대 + CMC(라즈베리파이) 개별 전원 ON/OFF 제어 화면."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._workers = []

        layout = QGridLayout(self)
        title = QLabel("전원 제어")
        title.setObjectName("screenTitle")
        layout.addWidget(title, 0, 0, 1, 4)

        row = 1
        self._status_labels = {}
        for i in range(len(settings.PDU_HOSTS)):
            row = self._add_row(
                layout,
                row,
                name=f"PDU-{i + 1}",
                key=f"pdu{i}",
                on_handler=lambda checked=False, idx=i: self._run_action(f"pdu{idx}", lambda: set_pdu_power(idx, True)),
                off_handler=lambda checked=False, idx=i: self._run_action(f"pdu{idx}", lambda: set_pdu_power(idx, False)),
                on_enabled=True,
            )

        self._add_row(
            layout,
            row,
            name="CMC (Pi)",
            key="cmc",
            on_handler=None,
            off_handler=lambda checked=False: self._run_action("cmc", lambda: set_cmc_power(False)),
            on_enabled=False,
            on_tooltip="라즈베리파이 자체는 소프트웨어로 다시 켤 수 없습니다.",
        )

    def _add_row(self, layout, row, name, key, on_handler, off_handler, on_enabled, on_tooltip=""):
        layout.addWidget(QLabel(name), row, 0)

        on_btn = QPushButton("ON")
        on_btn.setMinimumHeight(48)
        on_btn.setEnabled(on_enabled)
        if on_tooltip:
            on_btn.setToolTip(on_tooltip)
        if on_handler:
            on_btn.clicked.connect(on_handler)
        layout.addWidget(on_btn, row, 1)

        off_btn = QPushButton("OFF")
        off_btn.setMinimumHeight(48)
        off_btn.clicked.connect(off_handler)
        layout.addWidget(off_btn, row, 2)

        status_label = QLabel("")
        status_label.setObjectName("valueLabel")
        layout.addWidget(status_label, row, 3)
        self._status_labels[key] = status_label

        return row + 1

    def _run_action(self, key: str, fn):
        self._status_labels[key].setText("처리 중...")
        worker = ActionWorker(fn)
        worker.finished_with_result.connect(lambda ok, k=key: self._on_result(k, ok))
        worker.finished.connect(lambda w=worker: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(worker)
        worker.start()

    def _on_result(self, key: str, ok: bool):
        self._status_labels[key].setText("완료" if ok else "실패")
