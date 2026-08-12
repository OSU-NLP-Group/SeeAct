import base64
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

PACKAGE_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from seeact.demo_utils.inference_engine import engine_factory


class InferenceEngineTests(unittest.TestCase):
    def test_minimax_openai_configuration_preserves_model_and_base_url(self):
        engine = engine_factory(
            api_key="test-key",
            model="MiniMax-M3",
            protocol="openai",
            api_base="https://api.minimaxi.com/v1",
        )

        self.assertEqual(engine.model, "openai/MiniMax-M3")
        self.assertEqual(engine.api_base, "https://api.minimaxi.com/v1")
        self.assertEqual(engine.api_key, "test-key")

    def test_minimax_m27_is_registered(self):
        engine = engine_factory(
            api_key="test-key",
            model="MiniMax-M2.7",
            protocol="openai",
            api_base="https://api.minimax.io/v1",
        )

        self.assertEqual(engine.model, "openai/MiniMax-M2.7")

    def test_minimax_openai_generation_sends_screenshot_content(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            image_file.write(b"jpeg data")
            image_file.flush()

            response = SimpleNamespace(choices=[{"message": {"content": "CLICK"}}])
            with patch(
                    "seeact.demo_utils.inference_engine.litellm.completion",
                    return_value=response,
            ) as completion:
                engine = engine_factory(
                    api_key="test-key",
                    model="MiniMax-M3",
                    protocol="openai",
                    api_base="https://api.minimax.io/v1",
                )
                result = engine.generate(
                    prompt=["system", "describe the screenshot", "choose an action"],
                    image_path=image_file.name,
                )

        self.assertEqual(result, "CLICK")
        request = completion.call_args.kwargs
        self.assertEqual(request["model"], "openai/MiniMax-M3")
        self.assertEqual(request["api_base"], "https://api.minimax.io/v1")
        self.assertEqual(request["api_key"], "test-key")
        image_url = request["messages"][1]["content"][1]["image_url"]["url"]
        self.assertTrue(image_url.startswith("data:image/jpeg;base64,"))
        self.assertEqual(base64.b64decode(image_url.split(",", 1)[1]), b"jpeg data")

    def test_minimax_anthropic_configuration_sends_image_content(self):
        with tempfile.NamedTemporaryFile(suffix=".png") as image_file:
            image_file.write(b"png data")
            image_file.flush()

            class Response:
                def raise_for_status(self):
                    return None

                def json(self):
                    return {"content": [{"type": "text", "text": "CLICK"}]}

            with patch("seeact.demo_utils.inference_engine.httpx.post", return_value=Response()) as post:
                engine = engine_factory(
                    api_key="test-key",
                    model="MiniMax-M3",
                    protocol="anthropic",
                    anthropic_base_url="https://api.minimax.io/anthropic",
                )
                result = engine.generate(
                    prompt=["system", "describe the screenshot", "choose an action"],
                    image_path=image_file.name,
                )

        self.assertEqual(result, "CLICK")
        url, request = post.call_args.args[0], post.call_args.kwargs
        self.assertEqual(url, "https://api.minimax.io/anthropic/v1/messages")
        self.assertEqual(request["headers"]["x-api-key"], "test-key")
        image = request["json"]["messages"][0]["content"][1]
        self.assertEqual(image["type"], "image")
        self.assertEqual(image["source"]["media_type"], "image/png")
        self.assertEqual(base64.b64decode(image["source"]["data"]), b"png data")

    def test_minimax_anthropic_base_url_requires_anthropic_suffix(self):
        with self.assertRaisesRegex(ValueError, "must end with /anthropic"):
            engine_factory(
                api_key="test-key",
                model="MiniMax-M3",
                protocol="anthropic",
                anthropic_base_url="https://api.minimax.io/v1",
            )


if __name__ == "__main__":
    unittest.main()
