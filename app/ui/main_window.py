import logging

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.gpio_buttons import GpioButtonManager
from app.pdu_control import shutdown_pdu_outlet, shutdown_raspberry_pi
from app.ui.screen_info import InfoScreen
from app.ui.screen_pdu import PduScreen
from app.ui.screen_server import ServerScreen
from app.ui.screen_tank import TankScreen

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UniTank #2")

        self._stack = QStackedWidget()
        self._screens = {
            "rst": ServerScreen(),
            "tank": TankScreen(),
            "pdu": PduScreen(),
            "info": InfoScreen(),
        }
        for screen in self._screens.values():
            self._stack.addWidget(screen)

        nav_bar = self._build_nav_bar()

        central = QWidget()
        root_layout = QVBoxLayout(central)
        root_layout.addWidget(self._stack, stretch=1)
        root_layout.addWidget(nav_bar)
        self.setCentralWidget(central)

        self._show_screen("tank")

        self._gpio = GpioButtonManager(self)
        self._gpio.pwr_pressed.connect(self.on_pwr_pressed)
        self._gpio.rst_pressed.connect(lambda: self._show_screen("rst"))
        self._gpio.tank_pressed.connect(lambda: self._show_screen("tank"))
        self._gpio.pdu_pressed.connect(lambda: self._show_screen("pdu"))
        self._gpio.info_pressed.connect(lambda: self._show_screen("info"))

    def _build_nav_bar(self) -> QWidget:
        bar = QWidget()
        layout = QHBoxLayout(bar)

        buttons = [
            ("RST", lambda: self._show_screen("rst")),
            ("TANK", lambda: self._show_screen("tank")),
            ("PDU", lambda: self._show_screen("pdu")),
            ("INFO", lambda: self._show_screen("info")),
            ("PWR", self.on_pwr_pressed),
        ]
        for label, handler in buttons:
            btn = QPushButton(label)
            btn.setMinimumHeight(56)
            btn.clicked.connect(handler)
            layout.addWidget(btn)
        return bar

    def _show_screen(self, name: str):
        self._stack.setCurrentWidget(self._screens[name])

    def on_pwr_pressed(self):
        reply = QMessageBox.question(
            self,
            "전원 종료 확인",
            "라즈베리파이와 외부 장비(PDU) 전원을 종료합니다.\n계속하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        logger.warning("PWR 버튼: 전원 종료 절차 시작")
        shutdown_pdu_outlet()
        shutdown_raspberry_pi()

    def closeEvent(self, event):
        self._gpio.close()
        super().closeEvent(event)
