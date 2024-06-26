import argparse
from typing import List
import time, os, hashlib
import subprocess, shlex, signal
import re
from dataclasses import dataclass
import termcolor
import threading


from agent.conversation import Conversation, ImageTextConversation, Message
from agent.llm_utils import (
    chatgpt_completion,
    chatgpt_completion_async,
    gpt4v_completion,
)

from prompt import REACT_AGENT_SYSTEM_PROMPT
from agent.BaseAgent import BaseAgent


@dataclass
class ActionOutput:
    """
    This class is used to store the output of the action taken by the agent.
    """

    actionable: bool
    observation: str = ""
    action_type: str = None
    file_name: str = None


class ReActAgent(BaseAgent):
    """
    Refer to : https://arxiv.org/abs/2210.03629
    """

    def run(self, instruction: str, max_hop: int = 10, VERBOSE: bool = True) -> List:
        if VERBOSE:
            print(
                termcolor.colored(
                    f"# Instruction: {instruction}\n", "blue", attrs=["bold"]
                )
            )

        # Step 1: make code workspace
        self.workspace: str = (
            f"./workspace/{hashlib.md5(str(time.time()).encode()).hexdigest()}"
        )
        os.makedirs(self.workspace, exist_ok=True)

        # Step 2 : create initial conversation
        test_messages = [
            Message(role="system", text=REACT_AGENT_SYSTEM_PROMPT),
            Message(role="user", text=instruction),
        ]
        conversation = Conversation(messages=test_messages)

        # Step 3: Task Loop
        for i in range(max_hop):
            print_flag = False
            # Step 3-1 : get response from the model
            response_text = chatgpt_completion(conversation, self.model)
            conversation.add_message(Message(role="assistant", text=response_text))

            # Take action if possible
            action_out = self.take_action(response_text, VERBOSE=VERBOSE)
            conversation.add_message(Message(role="user", text=action_out.observation))
            if VERBOSE:
                print(
                    termcolor.colored(
                        f"# Observation: {action_out.observation}\n", "dark_grey"
                    )
                )
                if action_out.observation == "":
                    print_flag = True
                    print(termcolor.colored(f"Agent : {response_text}", "red"))

            if not action_out.actionable and not print_flag:
                if VERBOSE:
                    print(termcolor.colored(f"Agent : {response_text}", "yellow"))

            if "# Termin" in response_text[:33].strip():
                break

        return [response_text]

    def take_action(self, response: str, VERBOSE: bool = True):
        """
        This function takes the response from the agent and checks if it is actionable.
        """
        action_match = re.search(r"# Action\((WRITE|READ|RUN)\(([^)]+)\)\)", response)
        think_match = re.search(r"# Think", response)

        if think_match:
            think_content = re.search(r"# Think\n([\s\S]*)", response).group(1)
            if VERBOSE:
                print(termcolor.colored(f"# Think : \n{think_content}\n", "magenta"))
            return ActionOutput(
                actionable=True,
                action_type="Think",
                observation="Ok.",
            )

        if action_match:
            action_type = action_match.group(1)
            file_name = action_match.group(2)

            if VERBOSE:
                print(
                    termcolor.colored(
                        f"# Action {action_type}({file_name})",
                        "green",
                    )
                )

            if action_type == "WRITE":
                if action_type == "WRITE":
                    code_block_match = re.search(
                        r"```(?:html|css|js|python)\n([\s\S]*?)\n```", response
                    )
                    if code_block_match:
                        code_content = code_block_match.group(1)
                        if VERBOSE:
                            print(
                                termcolor.colored(
                                    f"\n{code_content}\n",
                                    "light_grey",
                                )
                            )
                        self.write_file(file_name, code_content)
                        return ActionOutput(
                            actionable=True,
                            action_type=action_type,
                            file_name=file_name,
                            observation=f"You have written the code to {file_name}",
                        )
                    else:
                        return ActionOutput(
                            actionable=False,
                            observation="You choose to write the file but did not provide the code block",
                        )

                # write the file on

            elif action_type == "READ":
                file_path = os.path.join(self.workspace, file_name)
                if os.path.exists(file_path):
                    with open(file_path, "r") as file:
                        content = file.read()
                    return ActionOutput(
                        actionable=True,
                        action_type=action_type,
                        file_name=file_name,
                        observation=f"Content of the file {file_name} : \n{content}",
                    )
                else:
                    return ActionOutput(
                        actionable=False,
                        observation=f"File {file_name} does not exist.",
                    )

            elif action_type == "RUN":
                # Run the file
                action_out = self.run_flask_app_with_tmux(file_name)
                return action_out

            return ActionOutput(
                actionable=True,
                action_type=action_type,
                file_name=file_name,
                observation="",
            )
        else:
            return ActionOutput(actionable=False)

    def write_file(self, file_name: str, content: str):
        file_path = os.path.join(self.workspace, file_name)
        with open(file_path, "w") as file:
            file.write(content)
        # print(f"File written: {file_path}")

    def run_flask_app_with_tmux(self, file_name: str) -> ActionOutput:
        file_path = os.path.join(self.workspace, file_name)
        session_name = "flask_app"

        # kill session if exists
        if os.system(f"tmux has-session -t {session_name}") == 0:
            os.system(f"tmux kill-session -t {session_name}")

        # Start the Flask app in a new detached tmux session
        start_command = f"tmux new -d -s {session_name} 'python3 {file_path}'"
        start_result = subprocess.run(start_command, shell=True)

        time.sleep(5)  # wait for the server to start
        capture_command = f"tmux capture-pane -p -S - -E - -t {session_name}"
        result = subprocess.run(
            capture_command, shell=True, text=True, capture_output=True
        )

        observation = (
            result.stdout.strip()
            if result.stdout.strip()
            else f"Running python3 {file_name} got no output."
        )

        return ActionOutput(
            actionable=True,
            action_type="RUN",
            file_name=file_name,
            observation=observation,
        )
