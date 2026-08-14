import logging

from PyQt6.QtCore import QObject, pyqtSignal

from app.config import settings

logger = logging.getLogger(__name__)


class GpioButtonManager(QObject):
    """물리 버튼 5개(PWR/RST/TANK/PDU/INFO)를 감시해 Qt 시그널로 변환한다.

    gpiozero 콜백은 별도 스레드에서 호출되므로, UI 코드를 직접 건드리지 않고
    반드시 시그널을 통해 메인(Qt) 스레드로 넘긴다.
    """

    pwr_pressed = pyqtSignal()
    rst_pressed = pyqtSignal()
    tank_pressed = pyqtSignal()
    pdu_pressed = pyqtSignal()
    info_pressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buttons = []
        if not settings.MOCK_MODE:
            self._setup_gpio()
        else:
            logger.info("MOCK_MODE: GPIO 버튼 비활성화, 화면상 네비게이션으로만 테스트 가능")

    def _setup_gpio(self):
        from gpiozero import Button

        pin_map = {
            settings.BUTTON_PIN_PWR: self.pwr_pressed,
            settings.BUTTON_PIN_RST: self.rst_pressed,
            settings.BUTTON_PIN_TANK: self.tank_pressed,
            settings.BUTTON_PIN_PDU: self.pdu_pressed,
            settings.BUTTON_PIN_INFO: self.info_pressed,
        }
        for pin, signal in pin_map.items():
            btn = Button(pin, pull_up=True, bounce_time=settings.BUTTON_BOUNCE_TIME)
            btn.when_pressed = signal.emit
            self._buttons.append(btn)
        logger.info("GPIO 버튼 초기화 완료: %s", list(pin_map.keys()))

    def close(self):
        for btn in self._buttons:
            btn.close()
