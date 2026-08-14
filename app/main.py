import logging
import sys

from PyQt6.QtWidgets import QApplication

from app.config import settings
from app.ui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


STYLE_SHEET = """
QWidget { background-color: #111827; color: #E5E7EB; font-size: 20px; }
#screenTitle { font-size: 28px; font-weight: bold; color: #60A5FA; padding-bottom: 12px; }
#cardTitle { font-size: 22px; font-weight: bold; color: #60A5FA; }
#valueLabel { font-size: 22px; font-weight: bold; color: #34D399; }
#warningLabel { font-size: 22px; font-weight: bold; color: #FBBF24; }
QFrame { border: 1px solid #374151; border-radius: 8px; padding: 8px; margin-bottom: 8px; }
QPushButton { background-color: #1F2937; border: 1px solid #374151; border-radius: 8px; padding: 8px; }
QPushButton:pressed { background-color: #374151; }
"""


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)

    window = MainWindow()
    if settings.MOCK_MODE:
        window.resize(800, 480)
        window.show()
    else:
        window.showFullScreen()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
