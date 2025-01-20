import json
import os

import fitz  # pymupdf

from agent.intelligence import extract_info_and_keywords

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(CURRENT_DIR, "../data")

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


class ResumeParser:
    def __init__(self, resume_file, num_search_queries):
        self.resume_file = resume_file
        self.num_search_queries = num_search_queries

    def parse_pdf_to_text(self):
        """Helper function to read PDF contents into a text string."""
        resume_file = self.resume_file

        if not resume_file:
            return ""

        filetype = os.path.splitext(resume_file.name)[-1]
        if filetype.lower() != ".pdf":
            raise ValueError(
                f"Only PDF files are supported at the moment. Got: {filetype}"
            )

        doc = fitz.open(filename=resume_file.name)
        text_content = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text(option="text")
            text_content += page_text

        return text_content

    def extract_keywords_for_search(
        self,
        provider: str = "openai",
        openai_model: str = "gpt-4",
        main_job_search_focus: str = "Data Scientist",
    ) -> None:
        """
        1) Reads the PDF text from the uploaded file
        2) Calls extract_info_and_keywords to do a single LLM pass:
        - Extract {positions}, {current_location}, {years_experience}, {skills}
        - Generate exactly `num_keywords` sets of job-search keywords
        3) Returns the extracted fields plus the sets as a multiline string
        """
        resume_file = self.resume_file
        num_keywords = self.num_search_queries

        if not resume_file:
            return "", "", 0, "", ""

        doc_text = self.parse_pdf_to_text()
        if not doc_text.strip():
            print("No text found in PDF.")
            return "", "", 0, "", "No text found in PDF."

        # Single pass to get everything
        k = int(num_keywords) if num_keywords else 20
        results = extract_info_and_keywords(
            resume_text=doc_text,
            k=k,
            provider=provider,
            openai_model=openai_model,
            main_job_search_focus=main_job_search_focus,
        )

        # Extract fields
        user_data = results[
            "user_data"
        ]  # {positions, current_location, years_experience, skills}
        work_history = user_data["work_history"]
        current_location = user_data.get("current_location", "")

        positions = []
        skills = []

        for job in work_history:
            positions.extend(job["Positions"])
            skills.extend(job["Relevant Skills"])

        # Convert years experience to integer if possible
        years_exp_str = user_data.get("years_experience", "")
        if isinstance(years_exp_str, str):
            if " " in years_exp_str:
                years_exp_str = years_exp_str.split()[0]
            years_experience_int = int(years_exp_str.strip())
        elif isinstance(years_exp_str, int):
            years_experience_int = years_exp_str
        else:
            print(f"\n❗  [AGENT] Invalid years experience: {years_exp_str}")

        # Convert the list of combos to a multiline string
        keyword_sets = results["keyword_sets"]
        combos_str = "\n".join(keyword_sets) if keyword_sets else ""

        user_data = {
            "positions": ", ".join(positions),
            "location": current_location,
            "years_experience": years_experience_int,
            "skills": ", ".join(skills),
            "keyword_combinations": combos_str,
        }

        user_data_path = os.path.join(SAVE_DIR, "user_data.json")

        print(
            f"\n👤  [AGENT] All necessary user data has been obtained and saved at: {user_data_path}"
        )

        # Save the extracted data to a json file
        with open(user_data_path, "w") as f:
            json.dump(user_data, f)

        return user_data
