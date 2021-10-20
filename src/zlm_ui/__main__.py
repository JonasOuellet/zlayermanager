import sys

import zlm_info
from zlm_ui import main_ui


if __name__ == "__main__":
    file_path = None
    for arg in sys.argv[1:3]:
        try:
            zlm_info.LAYER_INDEX = int(arg)
        except:
            file_path = arg

    app = main_ui.Qt.QApplication(sys.argv)
    ui = main_ui.ZlmMainUI(file_path)
    ui.show()
    sys.exit(app.exec_())
