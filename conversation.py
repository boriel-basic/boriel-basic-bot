from dataclasses import dataclass, asdict

from common import SYS_PROMPT, START, INST, SYS, ESYS, EINST, END


@dataclass(frozen=True)
class ConversationEntry:
    user_prompt: str
    system_answer: str


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

    def length(self, sys_prompt: str = SYS_PROMPT) -> int:
        return len(self.make_prompt("", sys_prompt))

    def truncate(self, max_length: int, sys_prompt: str = SYS_PROMPT) -> str:
        while self.length(sys_prompt) > max_length:
            self.pop()

        return self.make_prompt(sys_prompt)
