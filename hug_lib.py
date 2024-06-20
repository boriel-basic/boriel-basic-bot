import os

import requests


TOKEN = os.environ["TOKEN"]


def query(prompt: str, model: str = ""):
    model = model or "mistralai/Mistral-7B-Instruct-v0.3"
    # model = "microsoft/Phi-3-mini-4k-instruct"
    # model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {
        "inputs": prompt,
        "parameters": {
            "return_full_text": False,
            "max_new_tokens": 1024,
        },
        #    "wait_for_model": True,
    }

    response = requests.post(url=api_url, headers=headers, json=data)
    return response.json()


def get_embedding(sentence: str):
    model = "sentence-transformers/all-MiniLM-L6-v2"
    api_url = (
        f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}"
    )
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {"inputs": sentence}

    response = requests.post(url=api_url, headers=headers, json=data)
    return response.json()
