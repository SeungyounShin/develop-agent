import os
import openai
from openai import AsyncOpenAI

# change with your path
from agent.conversation import Conversation, ImageTextConversation, Message


def chatgpt_completion(conversation: Conversation, model: str = "gpt-3.5-turbo"):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages_for_api = conversation.to_openai_format()
    client = openai.OpenAI(api_key=openai.api_key)

    # Call the OpenAI API
    chat_completion = client.chat.completions.create(
        model=model, messages=messages_for_api
    )

    return chat_completion.choices[0].message.content


async def chatgpt_completion_async(
    conversation: Conversation,
    model: str = "gpt-3.5-turbo",
    max_tokens: int = 1024,
    top_p: float = 0.9,
    temperature: float = 0.1,
):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages_for_api = conversation.to_openai_format()
    async_client = AsyncOpenAI(api_key=openai.api_key)

    # Call the OpenAI API
    chat_completion = await async_client.chat.completions.create(
        model=model,
        messages=messages_for_api,
        max_tokens=max_tokens,
        top_p=top_p,
        temperature=temperature,
    )

    return chat_completion.choices[0].message.content


def gpt4v_completion(
    conversation: ImageTextConversation,
    model: str = "gpt-4-vision-preview",
    max_tokens: int = 1024,
    top_p: float = 0.9,
    temperature: float = 0.1,
):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages_for_api = conversation.to_openai_format()
    client = openai.OpenAI(api_key=openai.api_key)

    # Call the OpenAI API
    chat_completion = client.chat.completions.create(
        model=model,
        messages=messages_for_api,
        max_tokens=max_tokens,
        top_p=top_p,
        temperature=temperature,
    )

    return chat_completion.choices[0].message.content


async def gpt4v_completion_async(
    conversation: ImageTextConversation,
    model: str = "gpt-4-vision-preview",
    max_tokens: int = 512,
    top_p: float = 0.9,
    temperature: float = 0.1,
    VERBOSE: bool = False,
):
    # Asynchronous call for gpt4v
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages_for_api = conversation.to_openai_format()
    async_client = AsyncOpenAI(api_key=openai.api_key)

    if VERBOSE:
        print(f"User : ")
        print(conversation.messages[-1])

    chat_completion = await async_client.chat.completions.create(
        model=model,
        messages=messages_for_api,
        max_tokens=max_tokens,
        top_p=top_p,
        temperature=temperature,
    )

    if VERBOSE:
        print(f"Response : ")
        print(chat_completion.choices[0].message.content)

    return chat_completion.choices[0].message.content


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
    response_text = chatgpt_completion(conv)
    print(response_text)

    print("=" * 30)
    print("ImageText")
    print("=" * 30)

    conversation = ImageTextConversation(
        messages=[
            Message(role="system", text="Your are GPT4-Vision."),
            Message(
                role="user",
                text=f"What do you see?",
                image_path=f"./assets/web_image_test_0.png",
            ),
        ]
    )
    response_text = gpt4v_completion(conversation, max_tokens=512)
    print(response_text)
