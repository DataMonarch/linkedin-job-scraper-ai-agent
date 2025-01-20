# Local imports
import json
import re
import time
from typing import Any, Dict, List, Union

import urllib
from agent.prompts import (
    RESUME_INFO_EXTRACTOR_SYSTEM_PROMPT,
    RESUME_INFO_EXTRACTOR_USER_PROMPT,
    KEYWORD_GEN_SYSTEM_PROMPT,
    KEYWORD_GEN_USER_PROMPT,
    SMALL_INFO_EXTRACTOR_SYSTEM_PROMPT,
    SMALL_INFO_EXTRACTOR_USER_PROMPT,
    SMALL_LOCATION_EXTRACTOR_SYSTEM_PROMPT,
    SMALL_LOCATION_EXTRACTOR_USER_PROMPT,
)
from agent.llm import call_llm
import nltk

nltk.download("punkt")

WORD_TOKENIZER = nltk.tokenize.TreebankWordTokenizer()
MAX_WORDS_PER_CHUNK = 300

# Fields we expect in the final extracted text
EXTRACTION_FIELDS = ["positions", "current_location", "years_experience", "skills"]


def parse_gpt_extracted_info(extracted_text: str) -> Dict[str, str]:
    """
    Parse the four fields from the LLM response:
      {current_location}: ...
      {years_experience}: ...
      {positions}: ...
      {skills}: ...

    Returns a dict with keys: positions, current_location, years_experience, skills.
    """
    parsed_info = {}
    for field in EXTRACTION_FIELDS:
        # Example: substring = "{positions}:"
        substring = "{" + field + "}:"
        field_start = extracted_text.find(substring)
        if field_start == -1:
            parsed_info[field] = ""
            continue

        field_start += len(substring)
        field_end = extracted_text.find("\n", field_start)
        if field_end == -1:
            field_end = len(extracted_text)

        parsed_info[field] = extracted_text[field_start:field_end].strip()

    return parsed_info


def parse_gpt_keyword_sets(extracted_text: str, k: int) -> List[str]:
    """
    Parse the <Keywords> block from the LLM response to extract exactly k lines.
    The LLM output includes a section like:
      <Keywords>
      1) ...
      2) ...
      ...
      k) ...
      <\Keywords>
    We'll capture those lines and return them as a list of strings.
    """
    # Regex approach: we look for lines starting with "1) ...", "2) ...", etc.
    # We'll assume the LLM followed the prompt and put them in a <Keywords> block.
    # Let's find the section between <Keywords> and <\Keywords>
    pattern_block = r"<Keywords>(.*?)<\\Keywords>"
    block_match = re.search(pattern_block, extracted_text, re.DOTALL)
    if not block_match:
        return []

    keywords_block = block_match.group(1).strip()
    # Now parse each line that starts with "digit)" or something similar.
    lines = keywords_block.split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    # We only keep up to k lines
    results = []
    for line in lines:
        # e.g. "1) Software Engineer, Python"
        if ")" in line:
            parts = line.split(")", 1)
            if len(parts) > 1:
                line = parts[1].strip()
        results.append(line)

        if len(results) >= k:
            break

    return results


def parse_llm_json_output(llm_output: str) -> Union[Dict[str, Any], None]:
    """
    Parse the JSON output from the LLM API call.
    We expect a JSON object with the following keys:
      - "company_names": {company: {job_title, start_date, end_date}}
    """

    json_start = llm_output.find("{")
    json_end = llm_output.rfind("}")
    if json_start == -1 or json_end == -1:
        return None
    extracted_dict: str = llm_output[json_start : json_end + 1]
    extracted_dict: dict = json.loads(extracted_dict)

    return extracted_dict


def parse_mhop_location_info(llm_output: str) -> Dict[str, str]:
    """
    Parse the location information from the LLM response.
    The LLM response should be a JSON object with the following keys:
      - "current_location": ...
    """
    extracted_info = parse_llm_json_output(llm_output)

    current_location = extracted_info.get("current_location", "")

    return current_location


def parse_mhop_keywords_sets(llm_output: str) -> List[str]:
    """
    Parse the keyword information from the LLM response.
    The LLM response should be a JSON object with the following keys:
      - "keyword_sets": ...
    """
    extracted_info = parse_llm_json_output(llm_output)

    keyword_sets = extracted_info.get("keyword_sets", [])

    return keyword_sets


def parse_mhop_extracted_info(llm_outputs: List[str]) -> Dict[str, Any]:
    work_history = []

    for i, llm_output in enumerate(llm_outputs):
        extracted_dict = parse_llm_json_output(llm_output)
        if not extracted_dict:
            print(f"⚠️  [CHUNK {i}] No JSON found in LLM output.")
            continue
        companies_info: dict = extracted_dict.get("company_names", {})
        companies = list(companies_info.keys())

        work_history_current_chunk = []
        for company in companies:
            job_info = {
                "Company": company,
                "Job Title": companies_info[company].get("Positions", []),
                "Start Date": companies_info[company].get("Start Date", ""),
                "End Date": companies_info[company].get("End Date", ""),
                "Relevant Skills": companies_info[company].get("Relevant Skills", []),
            }
            work_history_current_chunk.append(job_info)

        work_history.extend(work_history_current_chunk)

    work_history_start_year = 3000
    work_history_end_year = 0

    for job in work_history:
        start_date = job.get("Start Date", "")
        end_date = job.get("End Date", "")

        if start_date:
            job_start_year = int(start_date.split("/")[-1])
            work_history_start_year = min(work_history_start_year, job_start_year)
        if end_date:
            if end_date.lower() == "present":
                work_history_end_year = time.localtime().tm_year
            else:
                job_end_year = int(end_date.split("/")[-1])
                work_history_end_year = max(work_history_end_year, job_end_year)

    total_experience = work_history_end_year - work_history_start_year

    return (work_history, total_experience)


def build_linkedin_url(
    keywords_line: str,
    location: str = "",
    posted_in_days: int = 7,
    easy_apply: bool = True,
) -> str:
    """
    Build a LinkedIn job search URL for a single line of keywords.
    The 'keywords_line' is something like: "Software Engineer, Python, Cloud"
    We'll convert that to "Software Engineer OR Python OR Cloud" in the query.
    location (str): e.g. "New York"
    posted_in_days (int): how many days to filter by (7=last week)

    Returns the full LinkedIn search URL.
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


def extract_info_and_keywords(
    resume_text: str,
    k: int = 20,
    provider: str = "openai",
    ollama_model: str = "llama3.2",
    openai_model: str = "gpt-4",
    main_job_search_focus: str = "Software Engineering",
) -> Dict[str, any]:
    """
    Single-pass LLM call:
      - Extract the 4 fields from the resume
      - Generate exactly k sets of keyword combos
      - Build LinkedIn URLs for each set

    Returns a dict with:
      {
        "user_data": {
           "work_history": List[Dict[str, str]],
           "current_location": str,
           "years_experience": str,
        },
        "keyword_sets": [list of str],  # e.g. ["1) Software Engineer, Python", "2) ..."]
        "keyword_urls": [list of str],  # corresponding LinkedIn URLs
      }
    """

    # Format the user prompt with the correct K and resume text

    user_data = {}
    print("\n🔍 [AGENT] Extracting resume fields...")

    if provider == "openai":
        location_response = call_llm(
            system_prompt=SMALL_LOCATION_EXTRACTOR_SYSTEM_PROMPT,
            user_prompt=SMALL_LOCATION_EXTRACTOR_USER_PROMPT.format(
                resume_text=resume_text
            ),
            provider=provider,
            ollama_model=ollama_model,
        )

        current_location = parse_mhop_location_info(location_response)
        user_data["current_location"] = current_location

        print("\n📝  [AGENT] Location extracted")

        llm_response = call_llm(
            system_prompt=SMALL_INFO_EXTRACTOR_SYSTEM_PROMPT,
            user_prompt=SMALL_INFO_EXTRACTOR_USER_PROMPT.format(resume_text),
            provider=provider,
            ollama_model=ollama_model,
            openai_model=openai_model,
        )

        work_history, total_experience = parse_mhop_extracted_info([llm_response])
        user_data["work_history"] = work_history
        print("\n📝  [AGENT] Work history extracted")
        user_data["years_experience"] = total_experience
        print("\n📝  [AGENT] Years of experience extracted")
    # TODO: Add support for Ollama
    elif provider == "ollama":
        tokenized_spans = list(WORD_TOKENIZER.span_tokenize(resume_text))
        num_chunks = len(tokenized_spans) // MAX_WORDS_PER_CHUNK
        resume_chunks = []

        for i in range(num_chunks):
            start, end = (
                tokenized_spans[i * MAX_WORDS_PER_CHUNK][0],
                tokenized_spans[(i + 1) * MAX_WORDS_PER_CHUNK][1],
            )
            resume_chunks.append(resume_text[start:end])

        # Add the last chunk
        resume_chunks.append(resume_text[end:])
        llm_outputs = []

        for i, chunk in enumerate(resume_chunks):
            print(f"🧩 [CHUNK {i}]\n {chunk}")

            if i == 0:
                location_response = call_llm(
                    system_prompt=SMALL_LOCATION_EXTRACTOR_SYSTEM_PROMPT,
                    user_prompt=SMALL_LOCATION_EXTRACTOR_USER_PROMPT.format(chunk),
                    provider=provider,
                    ollama_model=ollama_model,
                )

                print("#" * 20 + "\nLOCATION\n" + "#" * 20)
                print(location_response)
                llm_outputs.append(location_response)

            response = call_llm(
                system_prompt=RESUME_INFO_EXTRACTOR_SYSTEM_PROMPT,
                user_prompt=RESUME_INFO_EXTRACTOR_USER_PROMPT.format(chunk),
                provider=provider,
                ollama_model=ollama_model,
            )
            print("#" * 20 + "\nWORK EXPERIENCE\n" + "#" * 20)
            print(response)

            llm_outputs.append(response)

        llm_response = parse_mhop_extracted_info(llm_outputs)

    # Debug
    print("\n📝  [AGENT] User info extracted")

    print("\n🔍 [AGENT] Generating keyword sets...")

    keyword_request_response = call_llm(
        system_prompt=KEYWORD_GEN_SYSTEM_PROMPT,
        user_prompt=KEYWORD_GEN_USER_PROMPT.format(
            work_history=user_data.get("work_history", ""),
            main_job_search_focus=main_job_search_focus,
            k=k,
        ),
        provider=provider,
        openai_model=openai_model,
    )

    # Parse the k sets
    keyword_sets = parse_mhop_keywords_sets(keyword_request_response)

    print("\n📝  [AGENT] Keyword sets generated")

    posted_in_days = 7

    print("\n🔗  [AGENT] Generating LinkedIn URLs...")
    keyword_urls = []
    for keyword_set in keyword_sets:
        url = build_linkedin_url(
            keyword_set, location=current_location, posted_in_days=posted_in_days
        )
        keyword_urls.append(url)

    print("\n🔗  [AGENT] LinkedIn URLs generated")

    return {
        "user_data": user_data,
        "keyword_sets": keyword_sets,
        "keyword_urls": keyword_urls,
    }
