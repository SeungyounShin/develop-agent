import argparse
from abc import ABC, abstractmethod
from typing import List

# Import your existing modules
from agent.conversation import Conversation, ImageTextConversation, Message
from agent.llm_utils import (
    chatgpt_completion,
    chatgpt_completion_async,
    gpt4v_completion,
)

from prompt import SIMPLE_AGENT_SYSTEM_PROMPT
from agent.BaseAgent import BaseAgent

from typing import List


class SimpleCodeAgent(BaseAgent):

    def run(self, instruction: str, max_hop: int = 10) -> List:
        test_messages = [
            Message(role="system", text=SIMPLE_AGENT_SYSTEM_PROMPT),
            Message(role="user", text=instruction),
        ]
        # Create a Conversation instance with test messages
        conversation = Conversation(messages=test_messages)

        response_text = chatgpt_completion(conversation, self.model)

        return [response_text]
