import os

# Third-party imports
from ollama import chat, ChatResponse
import openai


# Setup OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", None)
OPENAI_AVAILABLE = openai.api_key is not None
if not OPENAI_AVAILABLE:
    print("OpenAI API key not found. Only Ollama will be used.")


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
            response = openai.chat.completions.create(
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
