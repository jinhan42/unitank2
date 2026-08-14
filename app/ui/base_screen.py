from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget

from app.config import settings
from app.ui.async_worker import AsyncWorker


class PollingScreen(QWidget):
    """일정 주기로 async collector를 호출해 화면을 갱신하는 화면의 베이스 클래스."""

    def __init__(self, collector_coro_factory, parent=None):
        super().__init__(parent)
        self._collector_coro_factory = collector_coro_factory
        self._worker: AsyncWorker | None = None

        self._timer = QTimer(self)
        self._timer.setInterval(settings.DATA_POLL_INTERVAL_SEC * 1000)
        self._timer.timeout.connect(self.poll_now)

    def showEvent(self, event):
        super().showEvent(event)
        self.poll_now()
        self._timer.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self._timer.stop()

    def poll_now(self):
        if self._worker is not None and self._worker.isRunning():
            return  # 이전 요청이 아직 진행 중이면 건너뜀
        self._worker = AsyncWorker(self._collector_coro_factory)
        self._worker.finished_with_result.connect(self.update_data)
        self._worker.start()

    def update_data(self, data: dict):
        raise NotImplementedError
