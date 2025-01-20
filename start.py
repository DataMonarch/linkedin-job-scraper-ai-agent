import sys
import os


def main():
    sys.path.append(os.path.join(os.getcwd(), "src"))
    if sys.platform == "win32":
        os.system("uv run src\\ui\\app.py")
    else:
        os.system("uv run src/ui/app.py")


if __name__ == "__main__":
    main()
