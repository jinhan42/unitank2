from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.gpio_buttons import GpioButtonManager
from app.ui.screen_info import InfoScreen
from app.ui.screen_pdu import PduScreen
from app.ui.screen_pwr import PowerControlScreen
from app.ui.screen_server import ServerScreen
from app.ui.screen_tank import TankScreen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UniTank #2")

        self._stack = QStackedWidget()
        self._screens = {
            "pwr": PowerControlScreen(),
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
        self._gpio.pwr_pressed.connect(lambda: self._show_screen("pwr"))
        self._gpio.rst_pressed.connect(lambda: self._show_screen("rst"))
        self._gpio.tank_pressed.connect(lambda: self._show_screen("tank"))
        self._gpio.pdu_pressed.connect(lambda: self._show_screen("pdu"))
        self._gpio.info_pressed.connect(lambda: self._show_screen("info"))

    def _build_nav_bar(self) -> QWidget:
        bar = QWidget()
        layout = QHBoxLayout(bar)

        buttons = [
            ("PWR", lambda: self._show_screen("pwr")),
            ("RST", lambda: self._show_screen("rst")),
            ("TANK", lambda: self._show_screen("tank")),
            ("PDU", lambda: self._show_screen("pdu")),
            ("INFO", lambda: self._show_screen("info")),
        ]
        for label, handler in buttons:
            btn = QPushButton(label)
            btn.setMinimumHeight(56)
            btn.clicked.connect(handler)
            layout.addWidget(btn)
        return bar

    def _show_screen(self, name: str):
        self._stack.setCurrentWidget(self._screens[name])

    def closeEvent(self, event):
        self._gpio.close()
        super().closeEvent(event)
