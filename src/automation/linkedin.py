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
USER_DATA_PATH = os.path.join(USER_DATA_DIR, "user_data.json")
JOBS_DATA_PATH = os.path.join(USER_DATA_DIR, "jobs_data.json")


class LinkedInAutomation:
    def __init__(self, headless: bool = False):
        self.headless: bool = headless
        self.base_platform_url: str = "https://www.linkedin.com/jobs/"
        self.browser_mgr = BrowserManager(headless=self.headless)
        self.search_url_list: list[str] = []
        self.build_search_list(days=7)
        self.user_data = json.load(open(USER_DATA_PATH))

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
        #         print("\nUser is still logging in...")
        #         print(e)

        print("\nUser is logged in successfully.")
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
                f"⚠️  >>> Scrollable container not found for selector: {container_selector}"
            )
            return

        scrollable_container = page.query_selector(container_selector)
        has_scroll = scrollable_container.evaluate(
            "element => element.scrollHeight > element.clientHeight"
        )

        if not has_scroll:
            print(
                f"⚠️  >>> Scrollable container not found for selector: {container_selector}"
            )
            return

        if not scrollable_container:
            print(
                f"⚠️  >>> Scrollable container not found for selector: {container_selector}"
            )
            return

        scroll_count = 0

        while scroll_count < max_scroll_attempts:
            # Get the container's current scrollHeight
            current_height = scrollable_container.evaluate("(el) => el.scrollHeight")

            # Scroll down by a certain increment
            scrollable_container.evaluate("(el) => { el.scrollTop += 1000; }")
            time.sleep(2)  # Wait briefly to allow new content to load

            new_height = scrollable_container.evaluate("(el) => el.scrollHeight")

            print(
                f"⬇️  [SCROLL] Scrolled to {new_height} pixels from {current_height} pixels."
            )

            if new_height == current_height:
                print("\n⛔ [SCROLL] Reached bottom or no further content.")
                break

            scroll_count += 1

        print(f"\n✅ [SCROLL] Completed {scroll_count} scroll attempts in container.")

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

        if "\n" in company_text:
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

    def _extract_and_classify_fields(self, page: Page) -> List[Dict[str, Any]]:
        """
        Collects all form fields on the Easy Apply step, classifies them, and returns
        a list of dictionaries with {'label': str, 'element': ElementHandle, 'type': str }.
        We'll skip certain fields by default (email, phone, resume).
        """

        # Identify the container that holds the form, from your snippet it might be `form`
        form_selector = "form"
        form_elm = page.query_selector(form_selector)
        if not form_elm:
            print("\n[EXTRACT] No <form> found on this step.")
            return []

        fields_info = []
        # We look for typical relevant elements:
        input_selectors = "input, select, textarea"
        input_elems = form_elm.query_selector_all(input_selectors)

        for elem in input_elems:
            # Classify this element
            ftype = self._classify_field(elem)
            # Extract label text if any
            label_txt = self._get_label_for_field(elem, form_elm)

            # If the label or placeholder is in our skip logic, we do NOT add it.
            if self._should_skip_field(label_txt, ftype):
                print(f"\n[SKIP] Skipping field '{label_txt}' of type '{ftype}'.")
                continue

            fields_info.append(
                {
                    "label": label_txt,
                    "element": elem,
                    "type": ftype,
                }
            )

        return fields_info

    def _classify_field(self, elem) -> str:
        """
        Basic classification by tagName/type attribute:
        - "text" => input[text], textarea
        - "dropdown" => select
        - "file" => input[file]
        - ...
        """
        tag_name = elem.evaluate("(el) => el.tagName.toLowerCase()")
        input_type = elem.get_attribute("type") or ""

        if tag_name == "select":
            return "dropdown"
        if tag_name == "textarea":
            return "text"
        if input_type in ["text", "tel", "email", "number"]:
            return "text"
        if input_type == "file":
            return "file"
        # fallback
        return "text"

    def _get_label_for_field(self, field_elm, form_elm) -> str:
        """
        Try to find the label text that belongs to this field.
        In your snippet, we see <label for="..."> or
        the label might be an immediate sibling or parent block with the text.

        We'll attempt the simplest approach:
        1) If 'id' is set on the field, check <label for="that id">.
        2) Otherwise, read the nearest .fb-dash-form-element__label or .artdeco-text-input--label
        """
        field_id = field_elm.get_attribute("id")
        if field_id:
            label = form_elm.query_selector(f"label[for='{field_id}']")
            if label:
                return label.inner_text().strip()

        # fallback: maybe check parent .fb-dash-form-element__label
        possible_label = field_elm.query_selector(
            "xpath=./ancestor::div[contains(@class,'fb-dash-form-element')]//label"
        )
        if possible_label:
            return possible_label.inner_text().strip()

        # fallback: placeholder
        placeholder = field_elm.get_attribute("placeholder")
        if placeholder:
            return placeholder.strip()

        return "Unknown Field"

    def _should_skip_field(self, label_text: str, field_type: str) -> bool:
        """
        Return True if we want to skip this field (email, phone, resume, etc.).
        We'll do partial match checks for safe measure.
        """
        label_lower = label_text.lower()
        if any(
            keyword in label_lower for keyword in ["email", "phone", "mobile", "resume"]
        ):
            return True
        # or skip file fields by type
        if field_type == "file":
            return True
        return False

    def _fill_fields(self, page: Page):
        """
        Extract and fill all fields in the current form step, skipping email/phone/resume.
        """
        fields_info = self._extract_and_classify_fields(page)

        for field in fields_info:
            label = field["label"]
            elem = field["element"]
            ftype = field["type"]
            # Some logic to produce an answer for each
            # For example, you might ask an LLM or just fill them with placeholders
            # We'll do a simple approach for demonstration
            answer = self._generate_answer_for_field(label, ftype)
            # Actually fill
            if ftype == "text":
                elem.fill(answer)
            elif ftype == "dropdown":
                self._select_dropdown_option(elem, answer)
            # add logic for checkboxes, radios, etc. if needed

    def _generate_answer_for_field(self, label: str, ftype: str) -> str:
        """
        Return a default answer or query an LLM.
        For demonstration, just return a placeholder for text or pick the first dropdown item.
        """

        # TODO: Add LLM logic here for real answers
        if ftype == "text":
            if "years" in label.lower():
                print("\n🔍 [ANSWER] Years of experience.")
                return self.user_data.get("years_experience", "0")

        elif ftype == "dropdown":
            return "United States (+1)"  # or some logic
        return ""

    def _select_dropdown_option(self, dropdown_elm, desired_text: str):
        """
        Finds an <option> whose text includes 'desired_text' and selects it.
        """
        options = dropdown_elm.query_selector_all("option")
        for opt in options:
            txt = opt.inner_text().strip()
            if desired_text.lower() in txt.lower():
                val = opt.get_attribute("value")
                if val:
                    dropdown_elm.select_option(val)
                    return
        # fallback: select first if no match
        if options:
            first_val = options[0].get_attribute("value")
            if first_val:
                dropdown_elm.select_option(first_val)

    def _apply_to_job(self, job_url: str, page: Page):
        """
        Navigates to the given job URL, looks for an Easy Apply button,
        and attempts to fill out the multi-step application form.

        Args:
            job_url (str): The URL of the job detail page.
            page (Page): The currently active Playwright page.
        """
        # 1) Go to the job detail URL
        print(f"\n[EASY APPLY] Navigating to job URL: {job_url}")
        page.goto(job_url, timeout=60_000)
        time.sleep(2)

        # 2) Check for the Easy Apply button
        # Typical selectors might be 'button.jobs-apply-button' or a data-control-name
        easy_apply_btn_selector = "button.jobs-apply-button"
        try:
            page.wait_for_selector(easy_apply_btn_selector, timeout=5000)
        except TimeoutError:
            print(f"\n⚠️  [EASY APPLY] No Easy Apply button found for job: {job_url}")
            return

        easy_apply_btn = page.query_selector(easy_apply_btn_selector)
        if not easy_apply_btn:
            print(f"\n⚠️  [EASY APPLY] No Easy Apply button found for job: {job_url}")
            return

        easy_apply_btn.click()
        time.sleep(2)

        form_completed = False

        while not form_completed:
            next_btn = page.query_selector("button[aria-label='Continue to next step']")
            review_btn = page.query_selector(
                "button[aria-label='Review your application']"
            )
            submit_btn = page.query_selector("button[aria-label='Submit application']")

            if submit_btn:
                print("\n✅ [EASY APPLY] Submitting application.")
                submit_btn.click()
                form_completed = True
                time.sleep(2)
            elif review_btn:
                print("\n🔄 [EASY APPLY] Reviewing application.")
                review_btn.click()
                time.sleep(2)
            elif next_btn:
                print("\n➡️ [EASY APPLY] Moving to next step.")
                next_btn.click()
                time.sleep(2)
            else:
                print(
                    "\n⚠️  [EASY APPLY] No next/review/submit button. Possibly done or blocked."
                )
                form_completed = True

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
            print(f"\n🌐 [NAVIGATION] Navigating to {url}")
            page.goto(url)
            time.sleep(2)

            self._scroll_through_jobs(page, max_scroll_attempts=5)

            # Example job-card selectors (these are illustrative; check actual LinkedIn DOM)
            job_card_selector = ".job-card-container"
            # Wait for the job cards to load
            try:
                page.wait_for_selector(job_card_selector, timeout=5000)
            except TimeoutError:
                print("\n⚠️  >>> Job cards not found on this page.")
                continue

            job_cards = page.query_selector_all(
                ".job-card-container"
            )  # or .job-card-container

            print(f"\n📃 >>> Found {len(job_cards)} job cards on this page.")

            for j, card in enumerate(job_cards):
                card.evaluate("(el) => { el.style.outline = '3px solid red'; }")
                # time.sleep(1)  # Optional short pause so the user can see the highlight

                job_info = self._parse_single_card(card)

                if job_info["job_id"] in scraped_job_ids:
                    print(
                        f"\n⚠️  [JOB PARSER] Skipping duplicate job: {job_info['title']}"
                    )
                    continue
                else:
                    scraped_job_ids.add(job_info["job_id"])

                all_jobs_data.append(job_info)

                print(
                    f"\n✅ [JOB PARSER] Scraped job {j + 1}/{len(job_cards)}: {job_info['title']}"
                )

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
