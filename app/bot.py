#!/usr/bin/env python3

import json
import os
import re
import sys
from collections import defaultdict
from enum import StrEnum
from typing import Final

import chromadb
import markdown
import telebot
from telebot.apihelper import ApiTelegramException
from telebot.types import Message

from .common import INSTRUCT_PROMPT_TEMPLATE, SYS_PROMPT, load_json, save_json
from .conversation import Conversation
from .lib.hugging_face import HuggingFaceApi

# LLM_MODEL: Final[str] = "HuggingFaceH4/zephyr-7b-beta"
LLM_MODEL: Final[str] = "mistralai/Mistral-7B-Instruct-v0.3"
# LLM_MODEL: Final[str] = "mistralai/Mistral-Nemo-Instruct-2407"


ALLOWED_USERS_FILE = "../.users.json"
ADMIN_USERS_FILE = ".admin_users.json"
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

CHROMA_DB_CLIENT: chromadb.ClientAPI
COLLECTION: chromadb.Collection

ALLOWED_USERS: dict[str, dict[str, bool]]

CONVERSATION_PATH: Final[str] = "./memory"
CONVERSATIONS = defaultdict(Conversation)
MAX_INPUT_LENGTH = 8192
HUGGINGFACE_API = HuggingFaceApi()


class Command(StrEnum):
    ADD_USER = "adduser"
    DEL_USER = "deluser"
    DEMOTE = "demote"
    HELP = "help"
    LIST = "listusers"
    PROMOTE = "promote"
    START = "start"


def is_user_allowed(message: Message) -> bool:
    return message.from_user.username in ALLOWED_USERS


def is_admin(message: Message) -> bool:
    return is_user_allowed(message) and ALLOWED_USERS[message.from_user.username].get("is_admin")


def escape_markdown(text: str, format_="markdown") -> str:
    if format_ == "html":
        text = markdown.markdown(text=text, output_format="html")
        text = text.replace("<p>", "")
        text = text.replace("</p>", "\n")
    else:
        code_blocks = re.findall(r"```.*?```", text, re.DOTALL)
        table = {i: patt for i, patt in enumerate(code_blocks)}
        for num, patt in table.items():
            text = text.replace(patt, rf"<code block: {num} \>")

        literals = re.findall("`.*?`|_.*?_", text)
        table |= {i: patt for i, patt in enumerate(literals, len(code_blocks))}
        for num, patt in enumerate(literals, len(code_blocks)):
            text = text.replace(patt, rf"<code block: {num} \>")

        text = telebot.formatting.escape_markdown(text)
        for num, patt in table.items():
            if patt.startswith("```\n"):
                patt = patt.replace("```", "```basic", 1)
            text = text.replace(rf"<code block: {num} \>", patt.replace("```\n", "````basic\n"))

    return text


def is_registered(user_id: str) -> bool:
    global ALLOWED_USERS
    return str(user_id) in ALLOWED_USERS


@bot.message_handler(commands=[Command.ADD_USER], func=is_admin)
def add_user(message: Message):
    # Check if a user ID was provided in the message
    if len(message.text.split()) < 2:
        bot.reply_to(message, f"Please provide a user ID to add. Usage: /{Command.ADD_USER} <user_id>")
        return

    new_user_id = message.text.split()[1].lstrip("@")
    if new_user_id not in ALLOWED_USERS:
        ALLOWED_USERS[new_user_id] = {"is_admin": False}
        save_json(ALLOWED_USERS_FILE, ALLOWED_USERS)
        bot.reply_to(message, f"User {new_user_id} has been added successfully.")
    else:
        bot.reply_to(message, f"User {new_user_id} is already in the list.")


@bot.message_handler(commands=[Command.DEL_USER], func=is_admin)
def del_user(message: Message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, f"Please provide a user ID to delete. Usage: /{Command.DEL_USER} <user_id>")
        return

    user_id = message.text.split()[1].lstrip("@")
    if user_id not in ALLOWED_USERS:
        bot.reply_to(message, f"User {user_id} is not in the list.")
    else:
        del ALLOWED_USERS[user_id]
        save_json(ALLOWED_USERS_FILE, ALLOWED_USERS)
        bot.reply_to(message, f"User {user_id} has been deleted successfully.")


@bot.message_handler(commands=[Command.LIST], func=is_admin)
def list_users(message: Message) -> None:
    bot.reply_to(message, f"```json\n{json.dumps(ALLOWED_USERS, indent=2)}\n```", parse_mode="MarkdownV2")


@bot.message_handler(commands=[Command.PROMOTE], func=is_admin)
def promote_user(message: Message) -> None:
    # Promotes a user to admin

    if len(message.text.split()) < 2:
        bot.reply_to(message, "Please provide a user ID to add. Usage: /adduser <user_id>")
        return

    new_user_id = message.text.split()[1]

    if new_user_id in ALLOWED_USERS:
        ALLOWED_USERS[new_user_id] = {"is_admin": True}
        save_json(ALLOWED_USERS_FILE, ALLOWED_USERS)
        bot.reply_to(message, f"User {new_user_id} has been promoted successfully.")
    else:
        bot.reply_to(message, f"User {new_user_id} is not in the list.")


@bot.message_handler(commands=[Command.DEMOTE], func=is_admin)
def demote_user(message: Message) -> None:
    # Demotes a user to normal user

    if len(message.text.split()) < 2:
        bot.reply_to(message, f"Please provide a user ID to add. Usage: /{Command.DEMOTE} <user_id>")
        return

    new_user_id = message.text.split()[1]

    if new_user_id in ALLOWED_USERS:
        ALLOWED_USERS[new_user_id] = {"is_admin": False}
        save_json(ALLOWED_USERS_FILE, ALLOWED_USERS)
        bot.reply_to(message, f"User {new_user_id} has been demoted successfully.")
    else:
        bot.reply_to(message, f"User {new_user_id} is not in the list.")


@bot.message_handler(commands=[Command.HELP], func=is_admin)
def command_help(message: Message) -> None:
    bot.reply_to(message, f"Available commands:\n * {'\n * '.join(Command)}")


@bot.message_handler(commands=[Command.START])
def start(message: Message) -> None:
    bot.reply_to(message, "Welcome to Boriel BASIC bot helper")
    message_id = message.chat.id
    if not is_user_allowed(message):
        bot.send_message(
            message_id, "I'm in demo / testing mode. You are not enrolled in the BETA.\nAsk @boriel to add you"
        )
        return

    bot.send_message(message_id, "You can ask me about Boriel BASIC doc, and code snippets.\nI'll try to do my best.")


def load_conversation(username: str) -> Conversation:
    global CONVERSATIONS

    if username not in CONVERSATIONS:
        conversation_json = load_json(f"{CONVERSATION_PATH}/{username}.json")

        if conversation_json:
            CONVERSATIONS[username] = Conversation.from_dict(conversation_json)

    return CONVERSATIONS[username]


def save_conversation(username: str, conversation: Conversation) -> None:
    save_json(f"{CONVERSATION_PATH}/{username}.json", conversation.as_dict())


@bot.message_handler(func=is_user_allowed)
def main_entry(message: Message) -> None:
    try:
        language = HUGGINGFACE_API.guess_language(message.text, LLM_MODEL)
        user_prompt = message.text

        # if language != "english":
        #     user_prompt = HUGGINGFACE_API.translate(message.text, target_lang="English", model=LLM_MODEL)

        # classification = HUGGINGFACE_API.zero_shot_classify(user_prompt, ("salutation", "clarification", "acknowledgement", "question", "task"))
        # print(classification)

        embedding = HUGGINGFACE_API.get_embedding(user_prompt)
        results = COLLECTION.query(query_embeddings=[embedding], n_results=3)
        data = "\n".join(f"\n\n{x[0]}" for i, x in enumerate(results["documents"], start=1))

        rag_prompt = INSTRUCT_PROMPT_TEMPLATE.format(data=data, user_prompt=user_prompt, language=language)
        username = message.from_user.username
        conversation = load_conversation(username)

        prompt = conversation.truncate(max_length=MAX_INPUT_LENGTH, user_prompt=rag_prompt, sys_prompt=SYS_PROMPT.format(language=language))
        print(prompt)

        output = HUGGINGFACE_API.query(model=LLM_MODEL, prompt=prompt)
        print(output)

        system_answer = output[0]["generated_text"]
        conversation.add_entry(user_prompt=user_prompt, system_answer=system_answer)
        save_conversation(username, conversation)
        # if language != "english":
        #     system_answer = HUGGINGFACE_API.translate(system_answer, target_lang=language.capitalize(), model=LLM_MODEL)

        try:
            escaped_msg = escape_markdown(system_answer, format_="markdown")
            bot.send_message(message.chat.id, escaped_msg, parse_mode="MarkdownV2")
        except ApiTelegramException as e:
            print(f"{e}")
            html = escape_markdown(system_answer, format_="html")
            try:
                bot.send_message(message.chat.id, html, parse_mode="HTML")
            except ApiTelegramException:
                bot.send_message(message.chat.id, system_answer)

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

    ALLOWED_USERS = load_json(ALLOWED_USERS_FILE)
    if not ALLOWED_USERS:
        ALLOWED_USERS = {
            "boriel": {
                "is_admin": True,
            },
        }
        save_json(ALLOWED_USERS_FILE, ALLOWED_USERS)


if __name__ == "__main__":
    main()
    bot.infinity_polling()
