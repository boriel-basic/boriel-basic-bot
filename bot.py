#!/usr/bin/env python3

import markdown
import os
import re
import sys

from collections import defaultdict

import telebot
import chromadb
from telebot.apihelper import ApiTelegramException

import hug_lib

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

CHROMA_DB_CLIENT: chromadb.ClientAPI
COLLECTION: chromadb.Collection

ALLOWED_USERS = {
    "boriel",
    "castarco",
    "Duefectu",
    "Ljg701",
    "SAYakimovich",
    "soyelrichar",
    "zxspectrum1984",
}

RE_INST = re.compile(r"\[INST].*\[/INST]", re.DOTALL)
RE_CLEAN = re.compile(r"^[ \t\n]*(<\|assistant\|>|ANSWER)?:?[ \t\n]*")
RE_S = re.compile(r"\[INST].*?\[/ASS]", re.DOTALL)

CONVERSATIONS = defaultdict(str)


def is_user_allowed(message) -> bool:
    return message.from_user.username in ALLOWED_USERS


def escape_markdown(text):
    text = markdown.markdown(text=text, output_format="html")
    text = text.replace("<p>", "")
    text = text.replace("</p>", "\n")

    return text


@bot.message_handler(func=is_user_allowed)
def main_entry(message):
    try:
        embedding = hug_lib.get_embedding(message.text)
        results = COLLECTION.query(query_embeddings=[embedding], n_results=3)
        data = "\n".join(
            f"SEARCH RESULT {i}:\n{x[0]}"
            for i, x in enumerate(results["documents"], start=1)
        )
        # print(results)

        username = message.from_user.username
        previous_prompt = CONVERSATIONS[username]
        while len(previous_prompt) > 4096:
            if not RE_S.search(previous_prompt):
                previous_prompt = ""
            previous_prompt = RE_S.sub("", previous_prompt, 1).strip()

        prompt = (
            f"{previous_prompt} [INST] Be brief an concise. The main topic is Boriel BASIC (a BASIC dialect derived from "
            f"Sinclair BASIC).\n{data}\n\n---\nQUESTION: {message.text}\n[/INST] [ASS]"
        )
        # print(prompt)

        output = hug_lib.query(model="HuggingFaceH4/zephyr-7b-beta", prompt=prompt)
        # print(output)

        CONVERSATIONS[username] = prompt + output[0]["generated_text"] + " [/ASS] "
        response = RE_INST.sub("", output[0]["generated_text"]).strip()
        response = RE_CLEAN.sub("", response)

        try:
            bot.send_message(message.chat.id, response, parse_mode="MarkdownV2")
        except ApiTelegramException:
            html = escape_markdown(response)
            try:
                bot.send_message(message.chat.id, html, parse_mode="HTML")
            except ApiTelegramException:
                bot.send_message(message.chat.id, response)

    except Exception as e:
        bot.send_message(message.chat.id, "Sorry, there was an error. Try again.")
        print(f"Error: {e}", file=sys.stderr)


def main():
    global COLLECTION
    global CHROMA_DB_CLIENT
    # load chromadb collection
    CHROMA_DB_CLIENT = chromadb.PersistentClient()
    COLLECTION = CHROMA_DB_CLIENT.get_collection("docs")


if __name__ == "__main__":
    main()
    bot.infinity_polling()
