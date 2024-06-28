#!/usr/bin/env python3

import json
import os
import re
import sys
from collections import defaultdict

import chromadb
import markdown
import telebot
from telebot.apihelper import ApiTelegramException

import hug_lib

ALLOWED_USERS_FILE = ".users.json"
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

CHROMA_DB_CLIENT: chromadb.ClientAPI
COLLECTION: chromadb.Collection

ALLOWED_USERS: set[str] = set()

RE_INST = re.compile(r"\[INST].*\[/INST]", re.DOTALL)
RE_CLEAN = re.compile(r"^[ \t\n]*(<\|assistant\|>|ANSWER)?:?[ \t\n]*")
RE_S = re.compile(r"\[INST].*?\[/ASS]", re.DOTALL)

CONVERSATIONS = defaultdict(str)


def load_allowed_users(fname: str) -> set[str]:
    if not os.path.isfile(fname):
        return set()

    with open(fname, "rt", encoding="utf-8") as f:
        return set(json.load(f))


def save_allowed_users(fname: str) -> None:
    with open(fname, "wt", encoding="utf-8") as f:
        json.dump(list(ALLOWED_USERS), f)



def is_user_allowed(message) -> bool:
    return message.from_user.username in ALLOWED_USERS


def escape_markdown(text):
    text = markdown.markdown(text=text, output_format="html")
    text = text.replace("<p>", "")
    text = text.replace("</p>", "\n")

    return text


def is_registered(user_id: str) -> bool:
    global ALLOWED_USERS
    return str(user_id) in ALLOWED_USERS


@bot.message_handler(commands=['adduser'], func=is_user_allowed)
def add_user(message):
    # Check if a user ID was provided in the message
    if len(message.text.split()) < 2:
        bot.reply_to(message, "Please provide a user ID to add. Usage: /adduser <user_id>")
        return

    new_user_id = message.text.split()[1]

    if new_user_id not in ALLOWED_USERS:
        ALLOWED_USERS.add(new_user_id)
        save_allowed_users(ALLOWED_USERS_FILE)
        bot.reply_to(message, f"User {new_user_id} has been added successfully.")
    else:
        bot.reply_to(message, f"User {new_user_id} is already in the list.")


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
    global ALLOWED_USERS
    global COLLECTION
    global CHROMA_DB_CLIENT

    # load chromadb collection
    CHROMA_DB_CLIENT = chromadb.PersistentClient()
    COLLECTION = CHROMA_DB_CLIENT.get_collection("docs")

    ALLOWED_USERS = load_allowed_users(ALLOWED_USERS_FILE)
    if not ALLOWED_USERS:
        ALLOWED_USERS = {"boriel"}
        save_allowed_users(ALLOWED_USERS_FILE)


if __name__ == "__main__":
    main()
    bot.infinity_polling()
