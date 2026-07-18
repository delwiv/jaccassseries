import os
import signal
import sys

from PySide6.QtCore import QTimer


def _setup_cuda() -> None:
    from src.stt.transcriber import _cublas_lib_path
    path = _cublas_lib_path()
    if not path:
        return
    import ctypes
    for fname in sorted(os.listdir(path)):
        if ".so" not in fname:
            continue
        try:
            ctypes.CDLL(os.path.join(path, fname))
        except OSError as e:
            print(f"[cuda] warning: could not load {fname}: {e}")


def main() -> None:
    _setup_cuda()

    from src.app import JacasseriesApp

    app = JacasseriesApp(sys.argv)

    signal.signal(signal.SIGINT, lambda *_: QTimer.singleShot(0, app.quit))

    app.run()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
