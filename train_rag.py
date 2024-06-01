#!/usr/bin/env python

import glob
import chromadb
import ollama

ZXBASIC_DOC_PATH = "/home/boriel/src/boriel-basic/zxbasic/docs"


def train(files: list[str]) -> None:
    client = chromadb.PersistentClient()
    collection = client.create_collection(name="docs")

    for i, filename in enumerate(files):
        print(f"Processing file {i+1}/{len(files)}: {filename}")

        try:
            with open(filename, "r") as f:
                doc = f.read()
                response = ollama.embeddings(model="mxbai-embed-large", prompt=doc)
                embedding = response["embedding"]
                collection.add(ids=[str(i)], embeddings=[embedding], documents=[doc])
        except Exception as e:
            print(f"Ignoring document {filename}\nException: {e}")


def main():
    files = glob.glob(f"{ZXBASIC_DOC_PATH.rstrip('/')}/**/*.md", recursive=True)
    train(files)


if __name__ == "__main__":
    main()
