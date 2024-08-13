from PySide6.QtCore import QObject, Signal


class WorkerSignals(QObject):
    login_done = Signal(str)