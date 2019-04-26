import sys

from zlm_ui import main_ui


if __name__ == "__main__":
    file_path = None
    if len(sys.argv) == 2:
        file_path = sys.argv[1]

    app = main_ui.Qt.QApplication(sys.argv)
    ui = main_ui.ZlmMainUI(file_path)
    ui.show()
    sys.exit(app.exec_())
