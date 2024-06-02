import os
import telebot
import chromadb
import ollama


BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

CHROMA_DB_CLIENT: chromadb.ClientAPI
COLLECTION: chromadb.Collection


@bot.message_handler()
def main_entry(message):
    response = ollama.embeddings(prompt=message.text, model="mxbai-embed-large")
    results = COLLECTION.query(query_embeddings=[response["embedding"]], n_results=1)
    data = results["documents"][0][0]
    print(results)
    output = ollama.generate(
        model="phi3",
        prompt=f"Respond to this prompt: {message.text}\n\nUsing this data: {data}.",
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
