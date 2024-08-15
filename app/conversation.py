from dataclasses import asdict, dataclass
from typing import Self

from .common import EINST, END, ESYS, INST, JSON, START, SYS, SYS_PROMPT


@dataclass(frozen=True)
class ConversationEntry:
    user_prompt: str
    system_answer: str

    def as_dict(self):
        return asdict(self)


@dataclass
class Conversation:
    dialog: list[ConversationEntry]

    def __init__(self):
        self.dialog = []

    def add_entry(self, user_prompt: str, system_answer: str) -> None:
        self.dialog.append(ConversationEntry(user_prompt, system_answer))

    def as_dict(self) -> dict[str, ConversationEntry]:
        return asdict(self)

    def pop(self, index: int = 0) -> ConversationEntry:
        return self.dialog.pop(index)

    def __len__(self) -> int:
        return len(self.dialog)

    def make_prompt(self, user_prompt: str, sys_prompt: str = SYS_PROMPT) -> str:
        result = f"{START}{INST} {SYS}\n{sys_prompt}\n{ESYS}\n"
        for i, entry in enumerate(self.dialog):
            if i > 0:
                result += f"{START}{INST}\n"

            result += f"{entry.user_prompt}\n{EINST}\n{entry.system_answer}{END}{START}{INST}\n"

        result = f"{result}\n{user_prompt}\n{EINST}"
        return result

    def length(self, user_prompt: str, sys_prompt: str = SYS_PROMPT) -> int:
        """Given a user_prompt and a system prompt, return the length of the conversation."""
        return len(self.make_prompt("", sys_prompt))

    def truncate(self, max_length: int, user_prompt: str, sys_prompt: str = SYS_PROMPT) -> str:
        """Given a user_prompt and a system prompt, truncate the conversation so its length
        is less than max_length."""
        while self.length(user_prompt, sys_prompt) > max_length:
            self.pop()

        return self.make_prompt(user_prompt, sys_prompt)

    @classmethod
    def from_dict(cls, data: JSON) -> Self:
        result = cls()
        for entry in data["dialog"]:
            result.add_entry(**entry)

        return result
