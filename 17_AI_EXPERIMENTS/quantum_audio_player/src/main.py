"""Entry point for the Quantum Audio Player application.

This module starts the PyQt6 application and shows the main window.
"""

import sys
from PyQt6.QtWidgets import QApplication

from player.ui import QuantumAudioPlayer


def main() -> None:
    """Launch the Quantum Audio Player GUI."""
    app = QApplication(sys.argv)
    window = QuantumAudioPlayer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()