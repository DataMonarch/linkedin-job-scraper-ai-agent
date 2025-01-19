import json
import os
import random
import time
import urllib.parse
from typing import Any, Dict, List

from playwright.sync_api import Page, TimeoutError

from automation.browser import BrowserManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(CURRENT_DIR, "..", "data")
JOBS_DATA_PATH = os.path.join(USER_DATA_DIR, "jobs_data.json")


class LinkedInAutomation:
    def __init__(self, headless: bool = False):
        self.headless: bool = headless
        self.base_platform_url: str = "https://www.linkedin.com/jobs/"
        self.browser_mgr = BrowserManager(headless=self.headless)
        self.search_url_list: list[str] = []
        self.build_search_list(days=7)

    def login_and_check(self):
        """User manually logs in, then we check something like the user profile icon.

        Returns:
            page: The Playwright page object after login.
        """
        page = self.browser_mgr.launch()
        page.goto(self.base_platform_url)

        # logged_in = False
        # while not logged_in:
        #     try:
        #         # Force navigation to the feed page in case it's not automatically redirected
        #         page.goto("https://www.linkedin.com/jobs/")

        #         # Wait for a selector that indicates the user is logged in.
        #         # Adjust this selector to something stable on the LinkedIn feed or 'Me' nav item.
        #         page.wait_for_selector(
        #             "a[data-control-name='nav.settings_view_profile']", timeout=3000
        #         )
        #         # If we reach here with no TimeoutError, user is logged in.
        #         logged_in = True

        #     except Exception as e:
        #         # The element wasn't found within 3 seconds; user still logging in
        #         # or there's a slow network. Sleep briefly and try again.
        #         time.sleep(2)
        #         print("User is still logging in...")
        #         print(e)

        print("User is logged in successfully.")
        return page

    def build_linkedin_url(
        self,
        keywords_line: str,
        location: str = "",
        posted_in_days: int = 7,
        easy_apply: bool = True,
    ) -> str:
        """
        Build a LinkedIn job search URL for a single line of keywords.

        Args:
            keywords_line (str): A line of keywords, e.g. "Software Engineer, Python, Cloud"
            location (str): e.g. "New York"
            posted_in_days (int): how many days to filter by (7=last week)
            easy_apply (bool): whether to filter by Easy Apply jobs

        Raises:
            ValueError: If the keywords_line is empty.

        Returns:
            str: The full LinkedIn search URL.

        """
        # Convert e.g. "Software Engineer, Python, Cloud" -> ["Software Engineer","Python","Cloud"]
        # Then join them with " OR "
        splitted = [s.strip() for s in keywords_line.split(",")]
        joined_keywords = " OR ".join(splitted)

        encoded_keywords = urllib.parse.quote_plus(joined_keywords)
        encoded_location = urllib.parse.quote_plus(location) if location else ""

        # r604800 = 7 days in seconds
        # for 14 days, that would be r1209600, etc.
        # We'll do a quick conversion:
        tpr_seconds = posted_in_days * 24 * 3600

        base_url = "https://www.linkedin.com/jobs/search/"
        final_url = (
            f"{base_url}?keywords={encoded_keywords}"
            f"&location={encoded_location}"
            f"&f_TPR=r{tpr_seconds}"
            f"&sortBy=DD"
        )

        if easy_apply:
            final_url += "&f_AL=true"

        return final_url

    def build_search_list(self, days: int):
        """Build a list of LinkedIn search URLs based on the user's keyword combinations.

        Args:
            days (int): Number of days to filter by (e.g. 7=last week).

        Returns:
            None
        """

        user_data = json.load(open(os.path.join(USER_DATA_DIR, "user_data.json")))
        custom_keywords = user_data["keyword_combinations"]
        location = user_data["location"]

        for line in custom_keywords.split("\n"):
            line = line.strip()
            if not line:
                continue

            url = self.build_linkedin_url(line, location=location, posted_in_days=days)
            self.search_url_list.append(url)

    def _scroll_through_jobs(
        self,
        page: Page,
        container_selector: str = ".UwxpnwBISmOFPIwyYXZPiisFfsyZrfpAIsaVTI",
        max_scroll_attempts: int = 10,
    ):
        """
        Scrolls the LinkedIn jobs container to load more job cards.

        Args:
            page (Page): The Playwright page object to scroll.
            container_selector (str): The CSS selector for the scrollable container.
            max_scroll_attempts (int): Maximum number of scroll passes to attempt.
        """
        try:
            page.wait_for_selector(container_selector, timeout=5000)
        except TimeoutError:
            print(
                f"⚠️ >>> Scrollable container not found for selector: {container_selector}"
            )
            return

        scrollable_container = page.query_selector(container_selector)
        has_scroll = scrollable_container.evaluate(
            "element => element.scrollHeight > element.clientHeight"
        )

        if not has_scroll:
            print(
                f"⚠️ >>> Scrollable container not found for selector: {container_selector}"
            )
            return

        if not scrollable_container:
            print(
                f"⚠️ >>> Scrollable container not found for selector: {container_selector}"
            )
            return

        last_scroll_height = 0
        scroll_count = 0

        while scroll_count < max_scroll_attempts:
            # Get the container's current scrollHeight
            current_height = scrollable_container.evaluate("(el) => el.scrollHeight")

            # Scroll down by a certain increment
            scrollable_container.evaluate("(el) => { el.scrollTop += 1000; }")
            time.sleep(2)  # Wait briefly to allow new content to load

            new_height = scrollable_container.evaluate("(el) => el.scrollHeight")

            print(
                f"[SCROLL] Scrolled to {new_height} pixels from {current_height} pixels."
            )

            if new_height == current_height:
                print("[SCROLL] Reached bottom or no further content.")
                break

            scroll_count += 1

        print(f"[SCROLL] Completed {scroll_count} scroll attempts in container.")

    def _parse_single_card(self, card) -> Dict[str, Any]:
        """
        Extracts information from a single job-card-container element.

        Args:
            card: The Playwright ElementHandle representing one job card.

        Returns:
            Dict[str, Any]: A dictionary containing job_id, title, company, etc.
        """
        job_id = card.get_attribute("data-job-id") or ""

        title_link = card.query_selector("a.job-card-container__link")
        title_text = ""
        job_url = ""
        if title_link:
            title_text = title_link.inner_text().strip()
            job_url = title_link.get_attribute("href") or ""
            if job_url.startswith("/"):
                job_url = urllib.parse.urljoin(self.base_platform_url, job_url)

        company_span = card.query_selector("div.artdeco-entity-lockup__subtitle span")
        company_text = company_span.inner_text().strip() if company_span else ""
        company_text = company_text.split("\n")[0].strip()

        location_li = card.query_selector(
            "div.artdeco-entity-lockup__caption ul.job-card-container__metadata-wrapper li"
        )
        loc_text = location_li.inner_text().strip() if location_li else ""

        benefits_li = card.query_selector(
            "div.mt1 ul.job-card-container__metadata-wrapper li"
        )
        benefits_text = benefits_li.inner_text().strip() if benefits_li else ""

        footer_items = card.query_selector_all(
            "ul.job-card-list__footer-wrapper li.job-card-container__footer-item"
        )
        footer_tags = [fi.inner_text().strip() for fi in footer_items if fi]

        job_info = {
            "job_id": job_id,
            "title": title_text,
            "company": company_text,
            "location": loc_text,
            "benefits": benefits_text,
            "footer_tags": footer_tags,
            "job_url": job_url,
        }
        return job_info

    def gather_job_listings(self, search_rate_limit: int = 2) -> List[Dict[str, Any]]:
        """
        For each URL in self.search_url_list:
         1. Navigate to the page
         2. Scrape job listings (title, company, location, link, easy apply presence, etc.)
         3. Return a list of dictionaries, each containing job details

        Args:
            search_rate_limit (int): The number of URLs to scrape before stopping.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing job details.
        """
        page = self.login_and_check()  # ensure user is logged in
        all_jobs_data = []
        scraped_job_ids = set()

        for i, url in enumerate(self.search_url_list):
            print(f"Navigating to {url}")
            page.goto(url)
            time.sleep(2)

            self._scroll_through_jobs(page, max_scroll_attempts=5)

            # Example job-card selectors (these are illustrative; check actual LinkedIn DOM)
            job_card_selector = ".job-card-container"
            # Wait for the job cards to load
            try:
                page.wait_for_selector(job_card_selector, timeout=5000)
            except TimeoutError:
                print("⚠️ >>> Job cards not found on this page.")
                continue

            job_cards = page.query_selector_all(
                ".job-card-container"
            )  # or .job-card-container

            print(f"📃 >>> Found {len(job_cards)} job cards on this page.")

            for j, card in enumerate(job_cards):
                job_info = self._parse_single_card(card)

                if job_info["job_id"] in scraped_job_ids:
                    print(f"⚠️ [JOB PARSER] Skipping duplicate job: {job_info['title']}")
                    continue
                else:
                    scraped_job_ids.add(job_info["job_id"])

                all_jobs_data.append(job_info)

                print("#" * 20 + f"\n Job {j + 1} \n" + "#" * 20)
                print(job_info)

            if i == search_rate_limit - 1:
                break

            # Sleep a random amount of time to avoid detection
            time.sleep(random.randint(2, 7))

        with open(JOBS_DATA_PATH, "w") as f:
            json.dump(all_jobs_data, f, indent=2)

        return all_jobs_data

    def close(self):
        self.browser_mgr.close()


def test_linkedin():
    li_auto = LinkedInAutomation(headless=False)
    li_auto.scrape_all_jobs()
    li_auto.close()


if __name__ == "__main__":
    test_linkedin()
