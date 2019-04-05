import sys

import mainUI


if __name__ == "__main__":
    file_path = None
    if len(sys.argv) == 2:
        file_path = sys.argv[1]

    app = mainUI.QtWidgets.QApplication(sys.argv)
    ui = mainUI.ZlmMainUI(file_path)
    ui.show()
    sys.exit(app.exec_())
