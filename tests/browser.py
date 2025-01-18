# In hello.py or a dedicated test file

from src.automation.browser import BrowserManager
import time


def test_browser():
    bm = BrowserManager(headless=False)
    page = bm.launch()
    page.goto("https://google.com")
    print("Page title:", page.title())
    time.sleep(2)  # allow some time to see the browser
    bm.close()


if __name__ == "__main__":
    test_browser()
