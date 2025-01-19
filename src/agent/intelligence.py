# Local imports
import re
from typing import Dict, List

import urllib
from .prompts import (
    RESUME_INFO_EXTRACTOR_SYSTEM_PROMPT,
    RESUME_INFO_EXTRACTOR_USER_PROMPT,
    KEYWORD_GEN_SYSTEM_PROMPT,
    KEYWORD_GEN_USER_PROMPT,
)
from .llm import call_llm

# Fields we expect in the final extracted text
EXTRACTION_FIELDS = ["positions", "current_location", "years_experience", "skills"]


def parse_extracted_info(extracted_text: str) -> Dict[str, str]:
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


def parse_keyword_sets(extracted_text: str, k: int) -> List[str]:
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
    ollama_model: str = "mistral",
    openai_model: str = "gpt-4",
) -> Dict[str, any]:
    """
    Single-pass LLM call:
      - Extract the 4 fields from the resume
      - Generate exactly k sets of keyword combos
      - Build LinkedIn URLs for each set

    Returns a dict with:
      {
        "parsed_fields": {
           "positions": str,
           "current_location": str,
           "years_experience": str,
           "skills": str
        },
        "keyword_sets": [list of str],  # e.g. ["1) Software Engineer, Python", "2) ..."]
        "keyword_urls": [list of str],  # corresponding LinkedIn URLs
      }
    """

    # Format the user prompt with the correct K and resume text
    user_prompt = RESUME_INFO_EXTRACTOR_USER_PROMPT.format(k=k, resume_text=resume_text)

    # We assume your system prompt doesn't need formatting for K (it references "K" conceptually).
    system_prompt = RESUME_INFO_EXTRACTOR_SYSTEM_PROMPT

    # Call LLM
    llm_response = call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        provider=provider,
        ollama_model=ollama_model,
        openai_model=openai_model,
    )

    # Debug
    print("[DEBUG] LLM Combined Output:\n", llm_response)

    # Parse fields
    parsed_fields = parse_extracted_info(llm_response)

    # Parse the k sets
    keyword_sets = parse_keyword_sets(llm_response, k)

    # Optionally build a LinkedIn URL for each set
    # We can incorporate the user's location from 'parsed_fields' if desired
    location = parsed_fields.get("current_location", "")
    # Or parse location out if it's e.g. "New York"
    posted_in_days = 7

    keyword_urls = []
    for line in keyword_sets:
        # Remove "1) ", "2) " prefix, if it exists
        # E.g. "1) Software Engineer, Python, Cloud"
        # We'll do a quick regex or parse
        cleaned_line = re.sub(r"^\d+\)\s*", "", line)
        url = build_linkedin_url(
            cleaned_line, location=location, posted_in_days=posted_in_days
        )
        keyword_urls.append(url)

    return {
        "parsed_fields": parsed_fields,
        "keyword_sets": keyword_sets,
        "keyword_urls": keyword_urls,
    }
