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
    "You are a nostalgic assistant which answer questions about Boriel BASIC using always human {language} language."
)

INSTRUCT_PROMPT_TEMPLATE: Final[
    str
] = """Given this prompt:\n\n
{user_prompt}

Answer it and give examples (if needed) only in Boriel BASIC (a BASIC programming language dialect).
Wrap code blocks using ```basic\n(the BASIC code)\n```. Answer informally like a person using {language} language.
The following data might be useful for context:
{data}
"""


def load_json(fname: str) -> JSON:
    if not os.path.isfile(fname):
        return dict()

    with open(fname, "rt", encoding="utf-8") as f:
        return json.load(f)


def save_json(fname: str, obj: JSON) -> None:
    with open(fname, "wt", encoding="utf-8") as f:
        json.dump(obj, f)
