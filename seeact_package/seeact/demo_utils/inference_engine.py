# -*- coding: utf-8 -*-
# Copyright (c) 2024 OSU Natural Language Processing Group
#
# Licensed under the OpenRAIL-S License;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.licenses.ai/ai-pubs-open-rails-vz1
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import time

import backoff
import openai
from openai import (
    APIConnectionError,
    APIError,
    RateLimitError,
)
import requests
from dotenv import load_dotenv
import litellm
import base64
import httpx
import mimetypes

EMPTY_API_KEY="Your API KEY Here"
MINIMAX_MODELS = {
    "minimax-m3": "MiniMax-M3",
    "minimax-m2.7": "MiniMax-M2.7",
}

def load_openai_api_key():
    load_dotenv()
    assert (
            os.getenv("OPENAI_API_KEY") is not None and
            os.getenv("OPENAI_API_KEY") != EMPTY_API_KEY
    ), "must pass on the api_key or set OPENAI_API_KEY in the environment"
    return os.getenv("OPENAI_API_KEY")


def load_gemini_api_key():
    load_dotenv()
    assert (
            os.getenv("GEMINI_API_KEY") is not None and
            os.getenv("GEMINI_API_KEY") != EMPTY_API_KEY
    ), "must pass on the api_key or set GEMINI_API_KEY in the environment"
    return os.getenv("GEMINI_API_KEY")


def load_minimax_api_key():
    load_dotenv()
    assert (
            os.getenv("MINIMAX_API_KEY") is not None and
            os.getenv("MINIMAX_API_KEY") != EMPTY_API_KEY
    ), "must pass on the api_key or set MINIMAX_API_KEY in the environment"
    return os.getenv("MINIMAX_API_KEY")


def resolve_minimax_base_url(protocol, configured_url):
    if configured_url is None:
        configured_url = os.getenv(
            "MINIMAX_ANTHROPIC_BASE_URL" if protocol == "anthropic" else "MINIMAX_API_BASE_URL"
        )
    if not configured_url:
        raise ValueError(
            "configure a MiniMax base URL with api_base or anthropic_base_url"
        )

    base_url = configured_url.rstrip("/")
    required_suffix = "/anthropic" if protocol == "anthropic" else "/v1"
    if not base_url.endswith(required_suffix):
        raise ValueError(f"MiniMax {protocol} base URL must end with {required_suffix}")
    return base_url

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def engine_factory(
        api_key=None,
        model=None,
        protocol="openai",
        api_base=None,
        anthropic_base_url=None,
        **kwargs,
):
    requested_model = model
    model = model.lower()
    if model in MINIMAX_MODELS:
        minimax_api_key = api_key if api_key and api_key != EMPTY_API_KEY else load_minimax_api_key()
        if protocol == "openai":
            return OpenAIEngine(
                model=f"openai/{MINIMAX_MODELS[model]}",
                api_key=minimax_api_key,
                api_base=resolve_minimax_base_url(protocol, api_base),
                **kwargs,
            )
        if protocol == "anthropic":
            return AnthropicEngine(
                model=MINIMAX_MODELS[model],
                api_key=minimax_api_key,
                api_base=resolve_minimax_base_url(protocol, anthropic_base_url),
                **kwargs,
            )
        raise ValueError("MiniMax protocol must be openai or anthropic")
    if model in ["gpt-4-vision-preview", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini"]:
        if api_key and api_key != EMPTY_API_KEY:
            os.environ["OPENAI_API_KEY"] = api_key
        else:
            load_openai_api_key()
        return OpenAIEngine(model=requested_model.lower(), **kwargs)
    elif model in ["gemini-1.5-pro-latest", "gemini-1.5-flash"]:
        if api_key and api_key != EMPTY_API_KEY:
            os.environ["GEMINI_API_KEY"] = api_key
        else:
            load_gemini_api_key()
        model=f"gemini/{model}"
        return GeminiEngine(model=model, **kwargs)
    elif model == "llava":
        model="llava"
        return OllamaEngine(model=model, **kwargs)
    raise Exception(f"Unsupported model: {model}, currently supported models: \
                    gpt-4-vision-preview, gpt-4-turbo, gpt-4o, , gpt-4o-mini, gemini-1.5-pro-latest, llava")

class Engine:
    def __init__(
            self,
            stop=["\n\n"],
            rate_limit=-1,
            model=None,
            temperature=0,
            api_key=None,
            api_base=None,
            **kwargs,
    ) -> None:
        """
            Base class to init an engine

        Args:
            api_key (_type_, optional): Auth key from OpenAI. Defaults to None.
            stop (list, optional): Tokens indicate stop of sequence. Defaults to ["\n"].
            rate_limit (int, optional): Max number of requests per minute. Defaults to -1.
            model (_type_, optional): Model family. Defaults to None.
        """
        self.time_slots = [0]
        self.stop = stop
        self.temperature = temperature
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        # convert rate limit to minmum request interval
        self.request_interval = 0 if rate_limit == -1 else 60.0 / rate_limit
        self.next_avil_time = [0] * len(self.time_slots)
        self.current_key_idx = 0
        print(f"Initializing model {self.model}")        

    def tokenize(self, input):
        return self.tokenizer(input)


class OllamaEngine(Engine):
    def __init__(self, **kwargs) -> None:
        """
            Init an Ollama engine
            To use Ollama, dowload and install Ollama from https://ollama.com/
            After Ollama start, pull llava with command: ollama pull llava
        """
        super().__init__(**kwargs)
        self.api_url = "http://localhost:11434/api/chat"


    def generate(self, prompt: list = None, max_new_tokens=4096, temperature=None, model=None, image_path=None,
                 ouput_0=None, turn_number=0, **kwargs):
        self.current_key_idx = (self.current_key_idx + 1) % len(self.time_slots)
        start_time = time.time()
        if (
                self.request_interval > 0
                and start_time < self.next_avil_time[self.current_key_idx]
        ):
            wait_time = self.next_avil_time[self.current_key_idx] - start_time
            print(f"Wait {wait_time} for rate limitting")
            time.sleep(wait_time)
        prompt0, prompt1, prompt2 = prompt

        base64_image = encode_image(image_path)
        if turn_number == 0:
            # Assume one turn dialogue
            prompt_input = [
                {"role": "assistant", "content": prompt0},
                {"role": "user", "content": prompt1, "images": [f"{base64_image}"]},
            ]
        elif turn_number == 1:
            prompt_input = [
                {"role": "assistant", "content": prompt0},
                {"role": "user", "content": prompt1, "images": [f"{base64_image}"]},
                {"role": "assistant", "content": f"\n\n{ouput_0}"},
                {"role": "user", "content": prompt2}, 
            ]

        options = {"temperature": self.temperature, "num_predict": max_new_tokens}
        data = {
            "model": self.model,
            "messages": prompt_input,
            "options": options,
            "stream": False,
        }
        _request = {
            "url": f"{self.api_url}",
            "json": data,
        }
        response = requests.post(**_request)  # type: ignore
        if response.status_code != 200:
            raise Exception(f"Ollama API Error: {response.status_code}, {response.text}")
        response_json = response.json()
        return response_json["message"]["content"]


class GeminiEngine(Engine):
    def __init__(self, **kwargs) -> None:
        """
            Init a Gemini engine
            To use this engine, please provide the GEMINI_API_KEY in the environment
            Supported Model             Rate Limit
            gemini-1.5-pro-latest    	2 queries per minute, 1000 queries per day
        """
        super().__init__(**kwargs)


    def generate(self, prompt: list = None, max_new_tokens=4096, temperature=None, model=None, image_path=None,
                 ouput_0=None, turn_number=0, **kwargs):
        self.current_key_idx = (self.current_key_idx + 1) % len(self.time_slots)
        start_time = time.time()
        if (
                self.request_interval > 0
                and start_time < self.next_avil_time[self.current_key_idx]
        ):
            wait_time = self.next_avil_time[self.current_key_idx] - start_time
            print(f"Wait {wait_time} for rate limitting")
        prompt0, prompt1, prompt2 = prompt
        litellm.set_verbose=True

        base64_image = encode_image(image_path)
        if turn_number == 0:
            # Assume one turn dialogue
            prompt_input = [
                {"role": "system", "content": prompt0},
                {"role": "user",
                 "content": [{"type": "text", "text": prompt1}, {"type": "image_url", "image_url": {"url": image_path,
                                                                                                    "detail": "high"},
                                                                }]},
            ]
        elif turn_number == 1:
            prompt_input = [
                {"role": "system", "content": prompt0},
                {"role": "user",
                 "content": [{"type": "text", "text": prompt1}, {"type": "image_url", "image_url": {"url": image_path,
                                                                                                    "detail": "high"}, 
                                                                }]},
                {"role": "assistant", "content": [{"type": "text", "text": f"\n\n{ouput_0}"}]},
                {"role": "user", "content": [{"type": "text", "text": prompt2}]}, 
            ]
        response = litellm.completion(
            model=model if model else self.model,
            messages=prompt_input,
            max_tokens=max_new_tokens if max_new_tokens else 4096,
            temperature=temperature if temperature else self.temperature,
            **kwargs,
        )
        return [choice["message"]["content"] for choice in response.choices][0]


class OpenAIEngine(Engine):
    def __init__(self, **kwargs) -> None:
        """
            Init an OpenAI GPT/Codex engine
            To find your OpenAI API key, visit https://platform.openai.com/api-keys
        """
        super().__init__(**kwargs)

    def _completion_kwargs(self, kwargs):
        completion_kwargs = dict(kwargs)
        if self.api_key is not None:
            completion_kwargs.setdefault("api_key", self.api_key)
        if self.api_base is not None:
            completion_kwargs.setdefault("api_base", self.api_base)
        return completion_kwargs

    @backoff.on_exception(
        backoff.expo,
        (APIError, RateLimitError, APIConnectionError),
    )
    def generate(self, prompt: list = None, max_new_tokens=4096, temperature=None, model=None, image_path=None,
                 ouput_0=None, turn_number=0, **kwargs):
        self.current_key_idx = (self.current_key_idx + 1) % len(self.time_slots)
        start_time = time.time()
        if (
                self.request_interval > 0
                and start_time < self.next_avil_time[self.current_key_idx]
        ):
            time.sleep(self.next_avil_time[self.current_key_idx] - start_time)
        prompt0, prompt1, prompt2 = prompt
        # litellm.set_verbose=True

        base64_image = encode_image(image_path)
        if turn_number == 0:
            # Assume one turn dialogue
            prompt_input = [
                {"role": "system", "content": [{"type": "text", "text": prompt0}]},
                {"role": "user",
                 "content": [{"type": "text", "text": prompt1}, {"type": "image_url", "image_url": {"url":
                                                                                                        f"data:image/jpeg;base64,{base64_image}",
                                                                                                    "detail": "high"},
                                                                 }]},
            ]
        elif turn_number == 1:
            prompt_input = [
                {"role": "system", "content": [{"type": "text", "text": prompt0}]},
                {"role": "user",
                 "content": [{"type": "text", "text": prompt1}, {"type": "image_url", "image_url": {"url":
                                                                                                        f"data:image/jpeg;base64,{base64_image}",
                                                                                                    "detail": "high"}, }]},
                {"role": "assistant", "content": [{"type": "text", "text": f"\n\n{ouput_0}"}]},
                {"role": "user", "content": [{"type": "text", "text": prompt2}]}, 
            ]
        response = litellm.completion(
            model=model if model else self.model,
            messages=prompt_input,
            max_tokens=max_new_tokens if max_new_tokens else 4096,
            temperature=temperature if temperature else self.temperature,
            **self._completion_kwargs(kwargs),
        )
        return [choice["message"]["content"] for choice in response.choices][0]


class AnthropicEngine(Engine):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if not self.api_key:
            raise ValueError("an API key is required for the Anthropic-compatible protocol")
        if not self.api_base or not self.api_base.endswith("/anthropic"):
            raise ValueError("the Anthropic-compatible base URL must end with /anthropic")

    def _message_content(self, prompt, image_path):
        content = [{"type": "text", "text": prompt}]
        if image_path:
            media_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": encode_image(image_path),
                },
            })
        return content

    def generate(self, prompt: list = None, max_new_tokens=4096, temperature=None, model=None, image_path=None,
                 ouput_0=None, turn_number=0, **kwargs):
        prompt0, prompt1, prompt2 = prompt
        if turn_number == 0:
            messages = [{"role": "user", "content": self._message_content(prompt1, image_path)}]
        elif turn_number == 1:
            messages = [
                {"role": "user", "content": self._message_content(prompt1, image_path)},
                {"role": "assistant", "content": f"\n\n{ouput_0}"},
                {"role": "user", "content": prompt2},
            ]
        else:
            raise ValueError("turn_number must be 0 or 1")

        payload = {
            "model": model if model else self.model,
            "system": prompt0,
            "messages": messages,
            "max_tokens": max_new_tokens if max_new_tokens else 4096,
            "temperature": temperature if temperature is not None else self.temperature,
        }
        response = httpx.post(
            f"{self.api_base}/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        content = response.json().get("content", [])
        return "".join(block.get("text", "") for block in content if block.get("type") == "text")


class OpenaiEngine_MindAct(Engine):
    def __init__(self, **kwargs) -> None:
        """Init an OpenAI GPT/Codex engine

        Args:
            api_key (_type_, optional): Auth key from OpenAI. Defaults to None.
            stop (list, optional): Tokens indicate stop of sequence. Defaults to ["\n"].
            rate_limit (int, optional): Max number of requests per minute. Defaults to -1.
            model (_type_, optional): Model family. Defaults to None.
        """
        super().__init__(**kwargs)
    #
    @backoff.on_exception(
        backoff.expo,
        (APIError, RateLimitError, APIConnectionError),
    )
    def generate(self, prompt, max_new_tokens=50, temperature=0, model=None, **kwargs):
        self.current_key_idx = (self.current_key_idx + 1) % len(self.time_slots)
        start_time = time.time()
        if (
                self.request_interval > 0
                and start_time < self.next_avil_time[self.current_key_idx]
        ):
            time.sleep(self.next_avil_time[self.current_key_idx] - start_time)
        if isinstance(prompt, str):
            # Assume one turn dialogue
            prompt = [
                {"role": "user", "content": prompt},
            ]
        response = litellm.completion(
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
