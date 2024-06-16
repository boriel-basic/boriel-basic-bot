import os
import chromadb
import ollama

CHROMA_DB_CLIENT: chromadb.ClientAPI
COLLECTION: chromadb.Collection


def main():
    global COLLECTION
    global CHROMA_DB_CLIENT
    # load chromadb collection
    CHROMA_DB_CLIENT = chromadb.PersistentClient()
    COLLECTION = CHROMA_DB_CLIENT.get_collection("docs")

    while True:
        prompt = input("Prompt: ")
        response = ollama.embeddings(prompt=prompt, model="nomic-embed-text")
        results = COLLECTION.query(
            query_embeddings=[response["embedding"]], n_results=3
        )
        print(len(results["documents"]))
        for result in results["documents"]:
            print(f"{result[0]}\n---")


if __name__ == "__main__":
    main()
