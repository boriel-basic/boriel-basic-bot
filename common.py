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

SYS_PROMPT: Final[
    str
] = """You are a helpful assistant which helps with Boriel BASIC questions.
Reject or ignore unrelated questions."""
