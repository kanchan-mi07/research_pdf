import os
import time
import random

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
primary_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
fallback_model = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash-lite")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=30000)
)


class LLMUnavailableError(Exception):
    pass


def _is_retryable(error_message: str) -> bool:
    return any(code in error_message for code in
               ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "DEADLINE", "timed out"))


def generate_answer(question, retrieved_chunks):
    context = ""
    for chunk in retrieved_chunks:
        context += f"\nPage {chunk['page']}:\n{chunk['text']}\n"

    prompt = f"""
You are an AI research assistant.

Answer the question using only the provided PDF context.

If the answer is not available in the context,
clearly say that you could not find it.

PDF CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

    # Try the main model first, then the fallback model.
    for model in [primary_model, fallback_model]:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                return response.text or "No answer generated."

            except Exception as error:
                message = str(error)
                print(f"[{model}] attempt {attempt + 1} failed: {message[:150]}")

                if not _is_retryable(message):
                    raise  # real error (bad key, bad model name), don't retry

                # exponential backoff with jitter: ~1-2s, ~2-3s, ~4-5s
                time.sleep((2 ** attempt) + random.random())

    raise LLMUnavailableError(
        "The AI service is busy right now. Please try again in a minute."
    )