from typing import Dict
import os

# Third-party imports
from ollama import chat, ChatResponse
import openai

# Local imports
from .prompts import (
    RESUME_INFO_EXTRACTOR_SYSTEM_PROMPT,
    RESUME_INFO_EXTRACTOR_USER_PROMPT,
)

# Setup OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", None)
OPENAI_AVAILABLE = openai.api_key is not None
if not OPENAI_AVAILABLE:
    print("OpenAI API key not found. Only Ollama will be used.")

# Fields we expect in the final extracted text
EXTRACTION_FIELDS = ["positions", "current_location", "years_experience", "skills"]


def call_llm(
    system_prompt: str,
    user_prompt: str,
    provider: str = "ollama",
    ollama_model: str = "mistral",
    openai_model: str = "gpt-4o-mini",
) -> str:
    """
    Generic LLM caller that can use either Ollama or OpenAI based on `provider`.

    Args:
        system_prompt (str): The system-level prompt (instructions, context).
        user_prompt (str): The user-level prompt (main content).
        provider (str): "ollama" or "openai".
        ollama_model (str): Name of the Ollama model to use (if provider=ollama).
        openai_model (str): Name of the OpenAI model to use (if provider=openai).

    Returns:
        str: The raw text response from the LLM.
    """
    if provider.lower() == "openai":
        if not OPENAI_AVAILABLE:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
            )

        try:
            response = openai.ChatCompletion.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"[OpenAI Error] {e}")
            return f"Error: {str(e)}"

    elif provider.lower() == "ollama":
        response: ChatResponse = chat(
            model=ollama_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response["message"]["content"]

    else:
        raise ValueError(
            f"Unknown provider '{provider}'. Must be 'ollama' or 'openai'."
        )


def parse_extracted_info(extracted_text: str) -> dict:
    """
    Parse the extracted information from the LLM response into a dictionary
    with keys: "positions", "current_location", "years_experience", "skills".

    The LLM is expected to output something like:
      {positions}: ...
      {current_location}: ...
      {years_experience}: ...
      {skills}: ...

    Args:
        extracted_text (str): The raw text from the LLM response.

    Returns:
        dict: A dictionary mapping each field to its extracted value.
    """
    parsed_info = {}
    for field in EXTRACTION_FIELDS:
        # e.g. substring = "{positions}:" => find that in the text
        substring = "{" + field + "}:"  # e.g., "{positions}:"
        field_start = extracted_text.find(substring)
        if field_start == -1:
            # Field not found; set empty
            parsed_info[field] = ""
            continue

        # Start after the substring
        field_start += len(substring)
        # End at next newline or end of string
        field_end = extracted_text.find("\n", field_start)
        if field_end == -1:
            field_end = len(extracted_text)

        parsed_info[field] = extracted_text[field_start:field_end].strip()

    return parsed_info


def extract_resume_info(
    resume_text: str,
    provider: str = "ollama",
    ollama_model: str = "mistral",
    openai_model: str = "gpt-4o-mini",
) -> Dict[str, str]:
    """
    Specialized function for extracting resume info using a specific system/user prompt.
    Leverages the generic `call_llm` and then parses the results for known fields.

    Args:
        resume_text (str): The raw resume text.
        provider (str): Which LLM provider ("ollama" or "openai").
        ollama_model (str): Ollama model name, if provider=ollama.
        openai_model (str): OpenAI model name, if provider=openai.

    Returns:
        Dict[str, str]: A dictionary with keys: "positions", "current_location",
                        "years_experience", "skills".
    """
    system_prompt = RESUME_INFO_EXTRACTOR_SYSTEM_PROMPT
    user_prompt = RESUME_INFO_EXTRACTOR_USER_PROMPT + resume_text

    # 1) Call the LLM
    llm_response = call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        provider=provider,
        ollama_model=ollama_model,
        openai_model=openai_model,
    )

    print(f"[DEBUG] LLM Raw Response:\n{llm_response}\n")

    # 2) Parse the response for known fields
    parsed_info = parse_extracted_info(llm_response)
    return parsed_info


if __name__ == "__main__":
    # Example usage
    resume_text = (
        "John Doe, Software Engineer, 5 years experience, location: Berlin, etc..."
    )
    info = extract_resume_info(
        resume_text=resume_text, provider="ollama", ollama_model="mistral"
    )
    print("[Ollama] Extracted info:", info)

    if OPENAI_AVAILABLE:
        info_openai = extract_resume_info(
            resume_text=resume_text, provider="openai", openai_model="gpt-4o-mini"
        )
        print("[OpenAI] Extracted info:", info_openai)
    else:
        print("OpenAI key not found; skipping OpenAI example.")
