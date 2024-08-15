# Tests the conversation library
from app.conversation import Conversation


class TestConversation:

    def setup_method(self):
        self.conversation = Conversation()

    def test_conversation(self):
        assert self.conversation is not None
        assert len(self.conversation) == 0

    def test_conversation_basic_prompt(self):
        prompt = self.conversation.make_prompt(user_prompt="A simple user prompt", sys_prompt="Generic system prompt")
        assert prompt == "<s>[INST] <<SYS>>\nGeneric system prompt\n" "<</SYS>>\n\nA simple user prompt\n[/INST]"

    def test_conversation_basic_answer(self):
        self.conversation.add_entry(user_prompt="User first prompt", system_answer="System first answer")
        assert len(self.conversation) == 1

        prompt = self.conversation.make_prompt(user_prompt="A simple user prompt", sys_prompt="Generic system prompt")
        assert prompt == (
            "<s>[INST] <<SYS>>\n"
            "Generic system prompt\n<</SYS>>\n"
            "User first prompt\n[/INST]\n"
            "System first answer</s><s>[INST]\n\n"
            "A simple user prompt\n[/INST]"
        )

    def test_conversation_truncation(self):
        max_length = 128  # characters
        for i in range(100):
            self.conversation.add_entry(user_prompt=f"User first prompt {i}", system_answer=f"System answer {i}")

        assert len(self.conversation) == 100

        prompt = self.conversation.truncate(
            max_length=max_length, user_prompt="A simple user prompt", sys_prompt="Generic sys prompt"
        )
        assert prompt == (
            "<s>[INST] <<SYS>>\n"
            "Generic sys prompt\n<</SYS>>\n"
            "User first prompt 99\n[/INST]\n"
            "System answer 99</s><s>[INST]\n\n"
            "A simple user prompt\n[/INST]"
        )
