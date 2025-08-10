import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from ui import ApiSnifferUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ApiSnifferUI()
    window.show()
    sys.exit(app.exec_())