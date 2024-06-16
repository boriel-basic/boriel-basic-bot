import os
import telebot
import chromadb
import ollama


BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

CHROMA_DB_CLIENT: chromadb.ClientAPI
COLLECTION: chromadb.Collection

ALLOWED_USERS = {"boriel", "Duefectu", "castarco", "soyelrichar"}


def is_user_allowed(message) -> bool:
    return message.from_user.username in ALLOWED_USERS


@bot.message_handler(func=is_user_allowed)
def main_entry(message):
    response = ollama.embeddings(prompt=message.text, model="nomic-embed-text")
    results = COLLECTION.query(query_embeddings=[response["embedding"]], n_results=3)
    data = "\n---\n".join(x[0] for x in results["documents"])
    print(results)
    output = ollama.generate(
        model="phi3",
        prompt=f"Be brief and concise. Answer this question about Boriel BASIC (a BASIC dialect derived from "
        f"Sinclair BASIC) and Respond to this prompt: {message.text}\n\nUsing this data: {data}.",
    )

    print(output)
    # bot.reply_to(message, message.text)
    bot.send_message(message.chat.id, output["response"])


def main():
    global COLLECTION
    global CHROMA_DB_CLIENT
    # load chromadb collection
    CHROMA_DB_CLIENT = chromadb.PersistentClient()
    COLLECTION = CHROMA_DB_CLIENT.get_collection("docs")


if __name__ == "__main__":
    main()
    bot.infinity_polling()
