import json
import os
from typing import Union

# Third-party imports
from ollama import chat, ChatResponse, AsyncClient
import openai
from agent.prompts import (
    SMALL_EXTRACTOR_SYSTEM_PROPMPT,
    SMALL_EXTRACTOR_USER_PROPMPT,
    SMALL_SUMMARIZER_SYSTEM_PROMPT,
    SMALL_SUMMARIZER_USER_PROMPT,
    SMALL_DATE_EXTRACTOR_SYSTEM_PROMPT,
    SMALL_DATE_EXTRACTOR_USER_PROMPT,
    SMALL_INFO_EXTRACTOR_SYSTEM_PROMPT,
    SMALL_INFO_EXTRACTOR_USER_PROMPT,
)


# Setup OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", None)
OPENAI_AVAILABLE = openai.api_key is not None
if not OPENAI_AVAILABLE:
    print("OpenAI API key not found. Only Ollama will be used.")


def call_llm(
    system_prompt: Union[str, None],
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

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    if provider.lower() == "openai":
        if not OPENAI_AVAILABLE:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
            )

        try:
            response = openai.chat.completions.create(
                model=openai_model,
                messages=messages,
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"[OpenAI Error] {e}")
            return f"Error: {str(e)}"

    elif provider.lower() == "ollama":
        response: ChatResponse = chat(
            model=ollama_model,
            messages=messages,
        )
        return response["message"]["content"]

    else:
        raise ValueError(
            f"Unknown provider '{provider}'. Must be 'ollama' or 'openai'."
        )


def main():
    import pymupdf as fitz
    import nltk

    nltk.download("punkt")

    word_tokenizer = nltk.tokenize.TreebankWordTokenizer()

    MAX_WORDS = 300

    current_dir = os.path.dirname(os.path.abspath(__file__))
    resume_file = os.path.join(current_dir, "..", "data", "resume.pdf")

    if not resume_file:
        return ""

    filetype = os.path.splitext(resume_file)[-1]
    if filetype.lower() != ".pdf":
        raise ValueError(f"Only PDF files are supported at the moment. Got: {filetype}")

    doc = fitz.open(filename=resume_file)
    resume_text = ""
    resume_chunks = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_text = page.get_text(option="text")

        tokenized_spans = word_tokenizer.span_tokenize(page_text)
        tokenized_spans = list(tokenized_spans)
        num_chunks = len(tokenized_spans) // MAX_WORDS
        for i in range(num_chunks):
            start, end = (
                tokenized_spans[i * MAX_WORDS][0],
                tokenized_spans[(i + 1) * MAX_WORDS][1],
            )
            resume_chunks.append(page_text[start:end])

        # Add the last chunk
        resume_chunks.append(page_text[end:])

    # summary = await call_llm(
    #     SMALL_SUMMARIZER_SYSTEM_PROMPT,
    #     SMALL_SUMMARIZER_USER_PROMPT.format(resume_text),
    #     provider="ollama",
    #     ollama_model="llama3.2",
    # )
    # print("#" * 20 + "\nSUMMARY\n" + "#" * 20)
    # print(summary)
    # print("_" * 100)
    # response = await call_llm(
    #     SMALL_EXTRACTOR_SYSTEM_PROPMPT,
    #     SMALL_EXTRACTOR_USER_PROPMPT.format(resume_text),
    #     provider="ollama",
    #     ollama_model="llama3.2",
    # )

    # print("#" * 20 + "\nWORK EXPERIENCE\n" + "#" * 20)
    # print(response)

    # date_response = await call_llm(
    #     SMALL_DATE_EXTRACTOR_SYSTEM_PROMPT,
    #     SMALL_DATE_EXTRACTOR_USER_PROMPT.format(resume_text),
    #     provider="ollama",
    #     ollama_model="llama3.2",
    # )

    # print("#" * 20 + "\nDATES\n" + "#" * 20)
    # print(date_response)

    for i, chunk in enumerate(resume_chunks):
        print(f"🧩 [CHUNK {i}]\n {chunk}")

        response = call_llm(
            SMALL_INFO_EXTRACTOR_SYSTEM_PROMPT,
            SMALL_INFO_EXTRACTOR_USER_PROMPT.format(chunk),
            provider="ollama",
            ollama_model="llama3.2",
        )
        print("#" * 20 + "\nWORK EXPERIENCE\n" + "#" * 20)
        print(response)
        
        json_start = response.find("{")
        json_end = response.rfind("}")
        if json_start == -1 or json_end == -1:
            continue
        extracted_dict: str = response[json_start : json_end + 1]
        extracted_dict: dict = json.loads(extracted_dict)
        
        print(extracted_dict)

    # company_response = await call_llm(
    #     POISITION_NAME_EXTRACTOR_SYSTEM_PROMPT,
    #     POISITION_NAME_EXTRACTOR_USER_PROMPT.format(resume_text),
    #     provider="ollama",
    #     ollama_model="llama3.2",
    # )

    # print("#" * 20 + "\nCOMPANIES\n" + "#" * 20)
    # print(company_response)


if __name__ == "__main__":
    main()
