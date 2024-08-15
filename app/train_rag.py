#!/usr/bin/env python3

import glob

import chromadb

from app.lib import hug_lib

ZXBASIC_DOC_PATH = "/home/boriel/src/boriel-basic/docs/doc"


def train(files: list[str]) -> None:
    client = chromadb.PersistentClient()
    collection = client.create_collection(
        name="docs", metadata={"hnsw:space": "cosine"}, get_or_create=True
    )

    for i, filename in enumerate(files):
        print(f"Processing file {i+1}/{len(files)}: {filename}")

        try:
            with open(filename, "rt", encoding="utf-8") as f:
                doc = f.read()
                # response = ollama.embeddings(model="nomic-embed-text", prompt=doc)
                # embedding = response["embedding"]
                embedding = hug_lib.get_embedding(doc)
                collection.add(ids=[str(i)], embeddings=[embedding], documents=[doc])
        except Exception as e:
            print(f"Ignoring document {filename}\nException: {e}")


def main():
    files = glob.glob(f"{ZXBASIC_DOC_PATH.rstrip('/')}/*.md", recursive=False)
    files += glob.glob(f"{ZXBASIC_DOC_PATH.rstrip('/')}/library/*.md", recursive=False)
    train(files)


if __name__ == "__main__":
    main()
