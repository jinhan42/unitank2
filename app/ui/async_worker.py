from PyQt6.QtCore import QThread, pyqtSignal


class AsyncWorker(QThread):
    """asyncio 코루틴 하나를 백그라운드 스레드에서 실행하고 결과를 시그널로 돌려준다.

    센서/BMC/SNMP 폴링이 네트워크 타임아웃으로 몇 초씩 걸릴 수 있으므로,
    UI(메인) 스레드를 막지 않기 위해 사용한다.
    """

    finished_with_result = pyqtSignal(dict)

    def __init__(self, coro_factory, parent=None):
        super().__init__(parent)
        self._coro_factory = coro_factory

    def run(self):
        import asyncio

        try:
            result = asyncio.run(self._coro_factory())
        except Exception as exc:  # noqa: BLE001
            result = {"connected": False, "error": str(exc)}
        self.finished_with_result.emit(result)
