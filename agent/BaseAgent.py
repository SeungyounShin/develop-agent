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

from prompt import *


class BaseAgent(ABC):
    def __init__(self, args):
        self.model = args.model

    @abstractmethod
    def run(self, instruction: str) -> List:
        """
        Runs the agent based on the given instruction.

        Parameters:
            instruction (str): The instruction or query to process.

        Returns:
            List: The response from the agent.
        """
        pass
