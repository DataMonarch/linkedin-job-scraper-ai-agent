import gradio as gr
import urllib.parse
import os

def parse_resume(resume_file) -> dict:
    """
    Stub function to parse a resume (PDF/text) for:
      - positions
      - location
      - years_experience
      - skills

    In production, you'd integrate an LLM or robust parser here.
    """
    
    print(f"Received resume file: {resume_file.name}")
    filetype, _ = os.path.splitext(resume_file.name)
    
    if not resume_file:
        return {
            "positions": [],
            "location": "",
            "years_experience": 0,
            "skills": []
        }

    # Example: read raw bytes, decode text
    content = resume_file.read()
    resume_text = content.decode("utf-8", errors="ignore")

    # TODO: implement ollama models to extract resume info

    # Mock data
    extracted_info = {
        "positions": ["Software Engineer", "Data Scientist"],  # from resume
        "location": "New York",
        "years_experience": 5,
        "skills": ["Python", "NLP", "Machine Learning"]
    }
    return extracted_info

def handle_resume_upload(resume):
    """
    Receives a file from the user,
    calls `parse_resume`, and returns extracted info for the UI.
    
    Args:
        resume (File): File uploaded by the user.
    Returns:
        Tuple of (positions_str, location, years_experience, skills_str)
    """
    if resume is None:
        return "", "", 0, ""

    info = parse_resume(resume)
    
    positions_str = ", ".join(info["positions"])
    location = info["location"]
    years_experience = info["years_experience"]
    skills_str = ", ".join(info["skills"])

    return positions_str, location, years_experience, skills_str

def build_linkedin_url(positions_str, location, years_experience, skills_str, custom_keywords):
    """
    Construct a LinkedIn job search URL for jobs posted in the last week (7 days),
    using the extracted data and any additional user-provided keywords.
    """
    # Combine positions + skills + custom keywords into a single list
    all_terms = []

    if positions_str.strip():
        pos_list = [p.strip() for p in positions_str.split(",")]
        all_terms.extend(pos_list)

    if skills_str.strip():
        skill_list = [s.strip() for s in skills_str.split(",")]
        all_terms.extend(skill_list)

    if custom_keywords.strip():
        custom_list = [k.strip() for k in custom_keywords.split(",")]
        all_terms.extend(custom_list)

    # Join them for the 'keywords' param, e.g. "Software Engineer OR Python OR NLP"
    if all_terms:
        joined_keywords = " OR ".join(all_terms)
    else:
        joined_keywords = ""

    encoded_keywords = urllib.parse.quote_plus(joined_keywords)
    encoded_location = urllib.parse.quote_plus(location) if location else ""

    # f_TPR=r604800 -> Posted in last week
    # sortBy=DD -> sort by date
    base_url = "https://www.linkedin.com/jobs/search/"
    final_url = (
        f"{base_url}?keywords={encoded_keywords}"
        f"&location={encoded_location}"
        f"&f_TPR=r604800"
        f"&sortBy=DD"
    )

    # In a production scenario, we might add more filters if needed
    return final_url

def gradio_app():
    with gr.Blocks() as demo:
        gr.Markdown("# Resume Analysis & LinkedIn Search (Last Week)")

        with gr.Row():
            with gr.Column():
                # 1) File upload
                resume_in = gr.File(label="Upload Resume (PDF or TXT)")
                analyze_btn = gr.Button("Analyze Resume")

            with gr.Column():
                # 2) Display extracted data (positions, location, yrs exp, skills)
                positions_box = gr.Textbox(label="Positions (comma-separated)")
                location_box = gr.Textbox(label="Location")
                years_box = gr.Number(label="Years of Experience")
                skills_box = gr.Textbox(label="Skills (comma-separated)")

        # Link the button to the parse function
        analyze_btn.click(
            fn=handle_resume_upload,
            inputs=[resume_in],
            outputs=[positions_box, location_box, years_box, skills_box]
        )

        # Additional custom keywords user might want
        gr.Markdown("### Add Extra Search Keywords (optional)")
        custom_keywords_box = gr.Textbox(label="Custom Keywords (comma-separated)")

        # Build URL
        build_btn = gr.Button("Build LinkedIn URL")
        linkedin_url_out = gr.Textbox(label="Resulting LinkedIn Search URL", interactive=False)

        build_btn.click(
            fn=build_linkedin_url,
            inputs=[positions_box, location_box, years_box, skills_box, custom_keywords_box],
            outputs=[linkedin_url_out]
        )

    return demo

if __name__ == "__main__":
    app = gradio_app()
    app.launch()
