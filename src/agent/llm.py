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
)


# Setup OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", None)
OPENAI_AVAILABLE = openai.api_key is not None
if not OPENAI_AVAILABLE:
    print("OpenAI API key not found. Only Ollama will be used.")


async def call_llm(
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
        response: ChatResponse = await AsyncClient().chat(
            model=ollama_model,
            messages=messages,
        )
        return response["message"]["content"]

    else:
        raise ValueError(
            f"Unknown provider '{provider}'. Must be 'ollama' or 'openai'."
        )


async def main():
    import pymupdf as fitz

    current_dir = os.path.dirname(os.path.abspath(__file__))
    resume_file = os.path.join(current_dir, "..", "data", "resume.pdf")

    if not resume_file:
        return ""

    filetype = os.path.splitext(resume_file)[-1]
    if filetype.lower() != ".pdf":
        raise ValueError(f"Only PDF files are supported at the moment. Got: {filetype}")

    doc = fitz.open(filename=resume_file)
    resume_text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_text = page.get_text(option="text")
        resume_text += page_text

    summary = await call_llm(
        SMALL_SUMMARIZER_SYSTEM_PROMPT,
        SMALL_SUMMARIZER_USER_PROMPT.format(resume_text),
        provider="ollama",
        ollama_model="llama3.2",
    )
    print("#" * 20 + "\nSUMMARY\n" + "#" * 20)
    print(summary)
    print("_" * 100)
    response = await call_llm(
        SMALL_EXTRACTOR_SYSTEM_PROPMPT,
        SMALL_EXTRACTOR_USER_PROPMPT.format(resume_text),
        provider="ollama",
        ollama_model="llama3.2",
    )

    print("#" * 20 + "\nWORK EXPERIENCE\n" + "#" * 20)
    print(response)

    date_response = await call_llm(
        SMALL_DATE_EXTRACTOR_SYSTEM_PROMPT,
        SMALL_DATE_EXTRACTOR_USER_PROMPT.format(resume_text),
        provider="ollama",
        ollama_model="llama3.2",
    )

    print("#" * 20 + "\nDATES\n" + "#" * 20)
    print(date_response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
