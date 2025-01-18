import time
from browser import BrowserManager


class LinkedInAutomation:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser_mgr = BrowserManager(headless=self.headless)

    def login_and_check(self):
        """User manually logs in, then we check something like the user profile icon."""
        page = self.browser_mgr.launch()
        page.goto("https://www.linkedin.com/login")

        logged_in = False
        while not logged_in:
            try:
                # Force navigation to the feed page in case it's not automatically redirected
                page.goto("https://www.linkedin.com/feed/")

                # Wait for a selector that indicates the user is logged in.
                # Adjust this selector to something stable on the LinkedIn feed or 'Me' nav item.
                page.wait_for_selector(
                    "a[data-control-name='nav.settings_view_profile']", timeout=3000
                )
                # If we reach here with no TimeoutError, user is logged in.
                logged_in = True

            except Exception as e:
                # The element wasn't found within 3 seconds; user still logging in
                # or there's a slow network. Sleep briefly and try again.
                time.sleep(2)
                print("User is still logging in...")

        print("User is logged in successfully.")
        return page

    def close(self):
        self.browser_mgr.close()


def test_linkedin():
    li_auto = LinkedInAutomation(headless=False)
    page = li_auto.login_and_check()
    li_auto.close()


if __name__ == "__main__":
    test_linkedin()
