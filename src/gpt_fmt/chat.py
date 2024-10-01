import os
from typing import Callable, Iterable, NotRequired, TypedDict, Unpack

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


class GptFmtChatOpts(TypedDict):
    model: str
    temperature: NotRequired[int]
    top_p: NotRequired[int | float]
    timeout: NotRequired[int]


GptFmtChatMessages = Iterable[ChatCompletionMessageParam]


class GptFmtChat:
    def __init__(self, **opts: Unpack[GptFmtChatOpts]):
        self.model = opts.get("model")
        self.temperature = opts.get("temperature")
        self.top_p = opts.get("top_p")
        self.timeout = opts.get("timeout")

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def complete(
        self,
        messages: GptFmtChatMessages,
        on_chunk: Callable[[str], None] | None = None,
        on_done: Callable[[str], None] | None = None,
    ):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            top_p=self.top_p,
            timeout=self.timeout,
            # we can theoretically disable this if we're not streaming the output,
            # but it doesn't seem to help at all with speed
            stream=True,
        )
        content = ""
        for chunk in completion:
            chunk_content = chunk.choices[0].delta.content
            if chunk_content is None:
                break
            content += chunk_content
            if on_chunk is not None:
                on_chunk(chunk_content)
        if on_done is not None:
            on_done(content)
        return content
