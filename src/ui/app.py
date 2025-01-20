import json
import os
import subprocess
import sys
from typing import List

import gradio as gr

from automation.linkedin import USER_DATA_DIR, LinkedInAutomation
from automation.resume_parser import ResumeParser


def open_chrome_with_remote_debugging():
    # Define the command based on the operating system
    if sys.platform == "win32":
        # Windows
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        command = f'"{chrome_path}" --remote-debugging-port=9222'
    elif sys.platform == "darwin":
        # macOS
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        command = f'"{chrome_path}" --remote-debugging-port=9222'
    else:
        # Linux and other platforms
        chrome_path = "google-chrome"
        command = f"{chrome_path} --remote-debugging-port=9222"

    try:
        # Launch Chrome with remote debugging
        subprocess.Popen(command, shell=True)
        print("\n🎮  [AGENT] Chrome launched with remote debugging on port 9222.")
    except Exception as e:
        print(f"\n🎮  [AGENT] Failed to launch Chrome: {e}")


USER_DATA_PATH = os.path.join(USER_DATA_DIR, "user_data.json")

LI_AUTO = LinkedInAutomation(headless=False)


def handle_resume_with_resumeparser(resume_file, num_keywords, main_job_search_focus):
    """
    1. Create a ResumeParser instance
    2. Call extract_keywords_for_search() => writes user_data.json
    3. Read user_data.json and return fields for display
    """
    if not resume_file:
        return "", "", 0, "", ""

    parser = ResumeParser(resume_file, num_keywords)
    parser.extract_keywords_for_search(
        main_job_search_focus=main_job_search_focus
    )  # saves user_data.json

    # read user_data.json
    if not os.path.exists(USER_DATA_PATH):
        return "", "", 0, "", "No data found after parsing."

    with open(USER_DATA_PATH, "r") as f:
        user_data = json.load(f)

    positions_str = user_data.get("positions", "")
    location_str = user_data.get("location", "")
    years_experience_int = user_data.get("years_experience", 0)
    skills_str = user_data.get("skills", "")
    combos_str = user_data.get("keyword_combinations", "")

    return positions_str, location_str, years_experience_int, skills_str, combos_str


def handle_scrape_jobs(search_rate_limit):
    """
    Instantiate LinkedInAutomation and gather job listings up to 'search_rate_limit' URLs.
    Return results in a 2D list for display in a DataFrame.
    """
    open_chrome_with_remote_debugging()

    li_auto = LinkedInAutomation(headless=False)  # or True if you prefer headless
    initial_search_urls = li_auto.search_url_list
    job_data = li_auto.gather_job_listings(search_rate_limit=search_rate_limit)

    li_auto.close()

    # Convert job_data (list of dicts) => list of rows
    rows = []
    # columns: [job_id, title, company, location, benefits, footer_tags, job_url]
    for job in job_data:
        job_id = job.get("job_id", "")
        title = job.get("title", "")
        company = job.get("company", "")
        location = job.get("location", "")
        benefits = job.get("benefits", "")
        footer_tags = ", ".join(job.get("footer_tags", []))
        job_url = job.get("job_url", "")
        rows.append([job_id, title, company, location, benefits, footer_tags, job_url])

    return rows, [
        [search_url] for search_url in initial_search_urls[:search_rate_limit]
    ]


def gradio_app():
    with gr.Blocks() as demo:
        gr.Markdown("# Single-Pass Resume Analysis & LinkedIn Scraping")

        # --- Resume Parsing & Keyword Generation ---
        with gr.Row():
            with gr.Column():
                resume_in = gr.File(label="Upload Resume (PDF only)")
                positions_box = gr.Textbox(label="Positions", interactive=True)
                skills_box = gr.Textbox(label="Skills", interactive=True)
                with gr.Row():
                    location_box = gr.Textbox(label="Location", interactive=True)
                    years_box = gr.Number(label="Years of Experience", interactive=True)
                combos_out = gr.Textbox(
                    label="Keyword Combinations", lines=8, interactive=True
                )

            with gr.Column():
                main_job_search_focus = gr.Textbox(
                    label="Main Job Search Focus", placeholder="e.g. Data Science"
                )
                num_keywords_box = gr.Number(
                    label="How many keyword combos?", value=5, precision=0
                )
                parse_btn = gr.Button("Analyze & Generate (ResumeParser)")
                gr.Markdown("### Scrape Job Listings")

                # Let user specify how many URLs from search_url_list to process
                scrape_limit_box = gr.Number(
                    label="Number of URLs to process", value=2, precision=0
                )
                scrape_btn = gr.Button("Scrape Jobs")

                urls_df = gr.DataFrame(
                    headers=["Search URLs"],
                    label="Generated LinkedIn Search URLs",
                    interactive=False,
                )

        # Callback: parse resume => user_data.json => display fields
        parse_btn.click(
            fn=handle_resume_with_resumeparser,
            inputs=[resume_in, num_keywords_box, main_job_search_focus],
            outputs=[positions_box, location_box, years_box, skills_box, combos_out],
        )

        job_table_out = gr.DataFrame(
            headers=[
                "job_id",
                "title",
                "company",
                "location",
                "benefits",
                "footer_tags",
                "job_url",
            ],
            label="Scraped Jobs",
            interactive=False,
        )

        # Callback: run LinkedInAutomation => gather_job_listings => show
        scrape_btn.click(
            fn=handle_scrape_jobs,
            inputs=[scrape_limit_box],
            outputs=[job_table_out, urls_df],
        )

    return demo


if __name__ == "__main__":
    app = gradio_app()
    app.launch()
