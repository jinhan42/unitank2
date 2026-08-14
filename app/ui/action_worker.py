from PyQt6.QtCore import QThread, pyqtSignal


class ActionWorker(QThread):
    """전원 제어처럼 결과가 필요한 동기 함수 하나를 백그라운드 스레드에서 실행한다.

    SNMP/subprocess 호출이 몇 초 걸릴 수 있으므로 UI(메인) 스레드를 막지 않기 위해 사용한다.
    """

    finished_with_result = pyqtSignal(bool)

    def __init__(self, fn, parent=None):
        super().__init__(parent)
        self._fn = fn

    def run(self):
        try:
            result = self._fn()
        except Exception:  # noqa: BLE001
            result = False
        self.finished_with_result.emit(bool(result))
