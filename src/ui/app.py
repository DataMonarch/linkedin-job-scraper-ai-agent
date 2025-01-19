import os
import json
from typing import List
import gradio as gr

from automation.resume_parser import ResumeParser
from automation.linkedin import LinkedInAutomation, USER_DATA_DIR

USER_DATA_PATH = os.path.join(USER_DATA_DIR, "user_data.json")


def handle_resume_with_resumeparser(resume_file, num_keywords):
    """
    1. Create a ResumeParser instance
    2. Call extract_keywords_for_search() => writes user_data.json
    3. Read user_data.json and return fields for display
    """
    if not resume_file:
        return "", "", 0, "", ""

    parser = ResumeParser(resume_file, num_keywords)
    parser.extract_keywords_for_search()  # saves user_data.json

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
    li_auto = LinkedInAutomation(headless=False)  # or True if you prefer headless
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

    return rows


def gradio_app():
    with gr.Blocks() as demo:
        gr.Markdown("# Single-Pass Resume Analysis & LinkedIn Scraping")

        # --- Resume Parsing & Keyword Generation ---
        with gr.Row():
            with gr.Column():
                resume_in = gr.File(label="Upload Resume (PDF only)")
                num_keywords_box = gr.Number(
                    label="How many keyword combos?", value=20, precision=0
                )
                parse_btn = gr.Button("Analyze & Generate (ResumeParser)")

            with gr.Column():
                positions_box = gr.Textbox(label="Positions")
                location_box = gr.Textbox(label="Location")
                years_box = gr.Number(label="Years of Experience")
                skills_box = gr.Textbox(label="Skills")
                combos_out = gr.Textbox(
                    label="Keyword Combinations", lines=8, interactive=False
                )

        # Callback: parse resume => user_data.json => display fields
        parse_btn.click(
            fn=handle_resume_with_resumeparser,
            inputs=[resume_in, num_keywords_box],
            outputs=[positions_box, location_box, years_box, skills_box, combos_out],
        )

        gr.Markdown("### Scrape Job Listings")

        # Let user specify how many URLs from search_url_list to process
        scrape_limit_box = gr.Number(
            label="Number of URLs to process", value=2, precision=0
        )
        scrape_btn = gr.Button("Scrape Jobs")
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
            outputs=[job_table_out],
        )

    return demo


if __name__ == "__main__":
    app = gradio_app()
    app.launch()
