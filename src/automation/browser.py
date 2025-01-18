from playwright.sync_api import sync_playwright


class BrowserManager:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser_context = None
        self.page = None

    def launch(self):
        self.playwright = sync_playwright().start()
        self.browser_context = self.playwright.chromium.launch_persistent_context(
            user_data_dir="./playwright_user_data", headless=self.headless
        )
        self.page = self.browser_context.new_page()
        return self.page

    def close(self):
        if self.browser_context:
            self.browser_context.close()
        if self.playwright:
            self.playwright.stop()
