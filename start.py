import sys
import os

sys.path.append(os.path.join(os.path.abspath(__file__), "src"))


def main():
    if sys.platform == "win32":
        os.system("uv run src\\ui\\app.py")
    else:
        os.system("uv run src/ui/app.py")


if __name__ == "__main__":
    main()
