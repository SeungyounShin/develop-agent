import os
import io, base64
from dataclasses import dataclass, field
from PIL import Image
from typing import List, Dict, Optional, Union


@dataclass
class Message:
    role: str
    text: Optional[str] = None
    image_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Union[str, Dict[str, str]]]:
        """Converts the message to a dictionary format expected by OpenAI API."""
        content = []
        if self.text:
            content.append({"type": "text", "text": self.text})
        if self.image_path:
            if isinstance(self.image_path, list):
                encoded_images = [self.encode_image(imgp) for imgp in self.image_path]
                for encoded_image in encoded_images:
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            },
                        }
                    )
            else:
                encoded_image = self.encode_image(self.image_path)
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                    }
                )
        return {"role": self.role, "content": content}

    @staticmethod
    def encode_image(image_path: str) -> str:
        """Encodes the image at the given path to base64. Compresses the image if it's larger than 20 MB."""

        initial_size = os.path.getsize(image_path)

        if initial_size > 20 * 1024 * 1024:
            # Open the image and compress
            with Image.open(image_path) as img:
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85, optimize=True)

                if buffer.getbuffer().nbytes > 20 * 1024 * 1024:
                    raise ValueError(
                        f"Unable to compress the image below 20 MB. [{image_path}]"
                    )
                return base64.b64encode(buffer.getvalue()).decode("utf-8")
        else:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")


@dataclass
class Conversation:
    messages: List[Message]

    def get_llama_style_prompt_string(self):
        prompt = ""
        for message in self.messages:
            if message.role.lower() == "system":
                prompt += f"<s>[INST] <<SYS>>\n{message.text}\n<</SYS>>\n\n"
            else:
                prompt += f"{message.text} [/INST]\n"
        return prompt

    def to_openai_format(self) -> List[Dict[str, str]]:
        formatted_messages = []
        for message in self.messages:
            formatted_messages.append({"role": message.role, "content": message.text})
        return formatted_messages

    def add_message(self, message: Message):
        self.messages.append(message)


@dataclass
class ImageTextConversation:
    messages: List[Message] = field(default_factory=list)

    def to_openai_format(
        self,
    ) -> List[Dict[str, Union[str, List[Dict[str, Union[str, Dict[str, str]]]]]]]:
        """Converts the conversation to a format suitable for OpenAI API."""
        return [message.to_dict() for message in self.messages]


if __name__ == "__main__":
    print("=" * 30)
    print("Text only")
    print("=" * 30)
    # Creating test messages
    test_messages = [
        Message(role="system", text="You are helpful robot."),
        Message(role="user", text="Hello, how are you?"),
        Message(role="assistant", text="I'm a bot, I'm doing great!"),
        Message(role="user", text="What can you do?"),
        Message(role="assistant", text="I can process data and respond to queries!"),
    ]

    # Creating a chat instance with the test messages
    conv = Conversation(messages=test_messages)

    # Generate the LLaMA style prompt string
    llama_style_prompt = conv.get_llama_style_prompt_string()
    print(llama_style_prompt)

    print("=" * 30)
    print("ImageText")
    print("=" * 30)

    conversation = ImageTextConversation(
        messages=[
            Message(role="system", text="I'm a bot, You have vision capability."),
            Message(
                role="user",
                text="Describe the pic.",
                image_path="./dataset/MagicBrush/source_img/9.jpg",
            ),
        ]
    )

    formatted_messages = conversation.to_openai_format()
    print(formatted_messages)
