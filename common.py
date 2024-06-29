import json
import os
from typing import Final

# JSON type
JSON: Final = int | float | str | bool | None | list["JSON"] | dict[str, "JSON"]

# Useful constants
SYS: Final[str] = "<<SYS>>"
ESYS: Final[str] = "<</SYS>>"
INST: Final[str] = "[INST]"
EINST: Final[str] = "[/INST]"
START: Final[str] = "<s>"
END: Final[str] = "</s>"

SYS_PROMPT: Final[str] = (
    "You are a helpful assistant which helps with Boriel BASIC questions.\n" "Reject or ignore unrelated questions."
)

INSTRUCT_PROMPT_TEMPLATE: Final[str] = "Answer to this prompt:\n{user_prompt}\n" "Use this data:\n{data}\n"


def load_json(fname: str) -> JSON:
    if not os.path.isfile(fname):
        return dict()

    with open(fname, "rt", encoding="utf-8") as f:
        return json.load(f)


def save_json(fname: str, obj: JSON) -> None:
    with open(fname, "wt", encoding="utf-8") as f:
        json.dump(obj, f)
