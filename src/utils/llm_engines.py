import os
import time

import backoff
import openai
from openai.error import (
    APIConnectionError,
    APIError,
    RateLimitError,
    ServiceUnavailableError,
)

class Engine:
    def __init__(self) -> None:
        pass

    def tokenize(self, input):
        return self.tokenizer(input)


class OpenaiEngine(Engine):
    def __init__(
            self,
            api_key=None,
            stop=["\n\n"],
            rate_limit=-1,
            model=None,
            temperature=0,
            **kwargs,
    ) -> None:
        """Init an OpenAI GPT/Codex engine

        Args:
            api_key (_type_, optional): Auth key from OpenAI. Defaults to None.
            stop (list, optional): Tokens indicate stop of sequence. Defaults to ["\n"].
            rate_limit (int, optional): Max number of requests per minute. Defaults to -1.
            model (_type_, optional): Model family. Defaults to None.
        """
        assert (
                os.getenv("OPENAI_API_KEY", api_key) is not None
        ), "must pass on the api_key or set OPENAI_API_KEY in the environment"
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY", api_key)
        if isinstance(api_key, str):
            self.api_keys = [api_key]
        elif isinstance(api_key, list):
            self.api_keys = api_key
        else:
            raise ValueError("api_key must be a string or list")
        self.stop = stop
        self.temperature = temperature
        self.model = model
        # convert rate limit to minmum request interval
        self.request_interval = 0 if rate_limit == -1 else 60.0 / rate_limit
        self.next_avil_time = [0] * len(self.api_keys)
        self.current_key_idx = 0
        Engine.__init__(self, **kwargs)

    @backoff.on_exception(
        backoff.expo,
        (APIError, RateLimitError, APIConnectionError, ServiceUnavailableError),
    )
    def generate(self, prompt, max_new_tokens=50, temperature=0, model=None, **kwargs):
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
        start_time = time.time()
        if (
                self.request_interval > 0
                and start_time < self.next_avil_time[self.current_key_idx]
        ):
            time.sleep(self.next_avil_time[self.current_key_idx] - start_time)
        openai.api_key = self.api_keys[self.current_key_idx]
        if isinstance(prompt, str):
            # Assume one turn dialogue
            prompt = [
                {"role": "user", "content": prompt},
            ]
        response = openai.ChatCompletion.create(
            model=model if model else self.model,
            messages=prompt,
            max_tokens=max_new_tokens,
            temperature=temperature,
            **kwargs,
        )
        if self.request_interval > 0:
            self.next_avil_time[self.current_key_idx] = (
                    max(start_time, self.next_avil_time[self.current_key_idx])
                    + self.request_interval
            )
        return [choice["message"]["content"] for choice in response["choices"]]