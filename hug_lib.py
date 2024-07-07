import os
from typing import Final

import requests

from common import JSON


DEFAULT_EMBEDDING_MODEL: Final[str] = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_QUERY_MODEL: Final[str] = "mistralai/Mistral-7B-Instruct-v0.3"


def resolve_token(token: str = "") -> str:
    return token or os.environ["TOKEN"]


def query(prompt: str, model: str = DEFAULT_QUERY_MODEL, api_token: str = "") -> JSON:
    token = resolve_token(api_token)
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "inputs": prompt,
        "parameters": {
            "return_full_text": False,
            "max_new_tokens": 1024,
            # "wait_for_model": True,
        },
    }

    response = requests.post(url=api_url, headers=headers, json=data)
    return response.json()


def get_embedding(sentence: str, embedding_model: str = DEFAULT_EMBEDDING_MODEL, api_token: str = "") -> JSON:
    """Given a sentence, return the embedding of the sentence."""
    token = resolve_token(api_token)
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{embedding_model}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"inputs": sentence}

    response = requests.post(url=api_url, headers=headers, json=data)
    return response.json()
