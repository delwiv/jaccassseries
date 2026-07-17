import sys
from src.app import JacasseriesApp


def main() -> None:
    app = JacasseriesApp(sys.argv)
    app.run()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
