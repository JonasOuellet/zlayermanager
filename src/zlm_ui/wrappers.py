from contextlib import contextmanager
import functools

from PyQt5 import QtWidgets, QtCore


@contextmanager
def wait_cursor():
    QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
    try:
        yield None
    finally:
        QtWidgets.QApplication.restoreOverrideCursor()


def do_with_wait_cursor(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        with wait_cursor():
            return fn(*args, **kwargs)
    return wrapper
