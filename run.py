from agent.conversation import Conversation, ImageTextConversation, Message
from agent.llm_utils import (
    chatgpt_completion,
    chatgpt_completion_async,
    gpt4v_completion,
)

from agent import SimpleCodeAgent, ReActAgent

AGENT_MAP = {"simple": SimpleCodeAgent, "react": ReActAgent}


def run(args):

    agent = AGENT_MAP[args.agent_type](args)

    responses = agent.run(args.instruction)

    for response in responses:
        print(response)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the agent.")
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4-turbo",
        help="The model to use for the conversation.",
    )
    parser.add_argument(
        "--instruction",
        type=str,
        default="Please develop a webpage that displays hello world.",
        help="The instruction to provide to the model.",
    )
    parser.add_argument(
        "--agent_type",
        type=str,
        default="simple",
        help="The type of agent to run (simple, react etc.).",
    )
    args = parser.parse_args()

    run(args)
