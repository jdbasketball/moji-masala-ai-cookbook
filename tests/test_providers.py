"""Protocol and SDK transport checks. No credentials or network calls needed."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from moji_demo import providers


PRODUCT_URL = "https://www.mojimasala.com/products/dahl-masala"
RECIPE_URL = "https://www.mojimasala.com/blogs/recipes/dahl-masala-recipe"
ARGUMENTS = {"dish": "dal", "vegan": False, "no_added_salt": False, "max_minutes": None, "single_spice": False}
RESULT = {"status": "matched", "matches": [{"product": {"product_url": PRODUCT_URL}, "recipe": {"url": RECIPE_URL}}], "message": "A matching recipe was found."}
ANSWER = "Use Dahl Masala with its own [dal recipe]({}).".format(RECIPE_URL)


class SequenceEndpoint:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(copy.deepcopy(kwargs))
        return next(self.responses)


def openai_call(arguments=None, name="match_recipes", call_id="call_1"):
    return SimpleNamespace(type="function_call", name=name, call_id=call_id,
                           arguments=json.dumps(ARGUMENTS) if arguments is None else arguments)


def openai_response(output=None, text=""):
    return SimpleNamespace(output=output or [], output_text=text)


def claude_call(arguments=None, name="match_recipes", call_id="toolu_1"):
    return {"type": "tool_use", "id": call_id, "name": name, "input": ARGUMENTS if arguments is None else arguments}


def claude_response(content=None, stop_reason="end_turn"):
    return SimpleNamespace(content=content or [], stop_reason=stop_reason)


class ProviderProtocolTests(unittest.TestCase):
    def test_openai_preserves_reasoning_and_correlates_tool_output(self):
        reasoning = SimpleNamespace(type="reasoning", encrypted_content="opaque_state", summary=[])
        call = openai_call()
        endpoint = SequenceEndpoint([openai_response([reasoning, call]), openai_response(text=ANSWER)])
        with patch.object(providers, "dispatch_tool", return_value=RESULT) as dispatch:
            answer = providers.run_openai("Help me make dal", client=SimpleNamespace(responses=endpoint))
        self.assertEqual(answer, ANSWER)
        dispatch.assert_called_once_with("match_recipes", ARGUMENTS)
        first, second = endpoint.calls
        self.assertEqual(first["tool_choice"], {"type": "function", "name": "match_recipes"})
        self.assertEqual(second["tool_choice"], "auto")
        self.assertFalse(first["store"])
        self.assertIn("reasoning.encrypted_content", first["include"])
        self.assertEqual(second["input"][1].encrypted_content, "opaque_state")
        output = second["input"][-1]
        self.assertEqual(output["call_id"], "call_1")
        self.assertEqual(json.loads(output["output"]), RESULT)

    def test_openai_bad_json_gets_a_tool_error_and_can_recover(self):
        endpoint = SequenceEndpoint([
            openai_response([openai_call(arguments="not json")]),
            openai_response([openai_call(call_id="call_2")]),
            openai_response(text=ANSWER),
        ])
        with patch.object(providers, "dispatch_tool", return_value=RESULT) as dispatch:
            self.assertEqual(providers.run_openai("dal", client=SimpleNamespace(responses=endpoint)), ANSWER)
        self.assertEqual(dispatch.call_count, 1)
        error = json.loads(endpoint.calls[1]["input"][-1]["output"])
        self.assertIn("valid JSON", error["error"])

    def test_openai_rejects_an_answer_that_skips_retrieval(self):
        endpoint = SequenceEndpoint([openai_response(text="Try this invented recipe")])
        with self.assertRaisesRegex(providers.ProviderError, "valid catalog lookup"):
            providers.run_openai("dal", client=SimpleNamespace(responses=endpoint))

    def test_rejects_generated_source_url_outside_tool_results(self):
        endpoint = SequenceEndpoint([
            openai_response([openai_call()]),
            openai_response(text="Recipe: https://www.mojimasala.com/invented-recipe"),
        ])
        with patch.object(providers, "dispatch_tool", return_value=RESULT):
            with self.assertRaisesRegex(providers.ProviderError, "URL that was not returned"):
                providers.run_openai("dal", client=SimpleNamespace(responses=endpoint))

    def test_sources_are_added_if_model_omits_requested_links(self):
        endpoint = SequenceEndpoint([openai_response([openai_call()]), openai_response(text="Use the matched recipe.")])
        with patch.object(providers, "dispatch_tool", return_value=RESULT):
            answer = providers.run_openai("dal", client=SimpleNamespace(responses=endpoint))
        self.assertIn(PRODUCT_URL, answer)
        self.assertIn(RECIPE_URL, answer)

    def test_no_match_does_not_require_or_invent_citations(self):
        endpoint = SequenceEndpoint([openai_response([openai_call()]), openai_response(text="No verified matching recipe is available.")])
        with patch.object(providers, "dispatch_tool", return_value={"status": "no_match", "matches": [], "message": "No match."}):
            answer = providers.run_openai("pizza", client=SimpleNamespace(responses=endpoint))
        self.assertNotIn("https:", answer)

    def test_claude_preserves_thinking_and_sends_results_immediately(self):
        thinking = {"type": "thinking", "thinking": "Check the catalog", "signature": "opaque_signature"}
        tool = claude_call()
        endpoint = SequenceEndpoint([
            claude_response([thinking, tool], "tool_use"),
            claude_response([{"type": "text", "text": ANSWER}]),
        ])
        with patch.object(providers, "dispatch_tool", return_value=RESULT):
            self.assertEqual(providers.run_claude("dal", client=SimpleNamespace(messages=endpoint)), ANSWER)
        first, second = endpoint.calls
        self.assertEqual(first["tool_choice"], {"type": "auto"})
        history = second["messages"]
        self.assertEqual(history[-2], {"role": "assistant", "content": [thinking, tool]})
        self.assertEqual(history[-1]["role"], "user")
        result = history[-1]["content"][0]
        self.assertEqual(result["tool_use_id"], "toolu_1")
        self.assertFalse(result["is_error"])
        self.assertEqual(json.loads(result["content"]), RESULT)

    def test_claude_unknown_tool_error_is_returned_and_can_recover(self):
        endpoint = SequenceEndpoint([
            claude_response([claude_call(name="invented_tool")], "tool_use"),
            claude_response([claude_call(call_id="toolu_2")], "tool_use"),
            claude_response([{"type": "text", "text": ANSWER}]),
        ])
        def dispatch(name, args):
            return {"error": "Unknown tool."} if name != "match_recipes" else RESULT
        with patch.object(providers, "dispatch_tool", side_effect=dispatch):
            providers.run_claude("dal", client=SimpleNamespace(messages=endpoint))
        self.assertTrue(endpoint.calls[1]["messages"][-1]["content"][0]["is_error"])

    def test_claude_rejects_an_answer_that_skips_retrieval(self):
        endpoint = SequenceEndpoint([claude_response([{"type": "text", "text": "Trust my recipe"}])])
        with self.assertRaisesRegex(providers.ProviderError, "valid catalog lookup"):
            providers.run_claude("dal", client=SimpleNamespace(messages=endpoint))

    def test_truncated_claude_response_is_not_returned_as_complete(self):
        endpoint = SequenceEndpoint([
            claude_response([claude_call()], "tool_use"),
            claude_response([{"type": "text", "text": "Here is half a recipe"}], "max_tokens"),
        ])
        with patch.object(providers, "dispatch_tool", return_value=RESULT):
            with self.assertRaisesRegex(providers.ProviderError, "token limit"):
                providers.run_claude("dal", client=SimpleNamespace(messages=endpoint))

    def test_incomplete_openai_response_is_not_returned_as_complete(self):
        incomplete = openai_response(text="Here is half a recipe")
        incomplete.status = "incomplete"
        endpoint = SequenceEndpoint([openai_response([openai_call()]), incomplete])
        with patch.object(providers, "dispatch_tool", return_value=RESULT):
            with self.assertRaisesRegex(providers.ProviderError, "stopped before completing"):
                providers.run_openai("dal", client=SimpleNamespace(responses=endpoint))

    def test_tool_round_limits_bound_provider_calls(self):
        for provider in ("openai", "claude"):
            with self.subTest(provider=provider):
                if provider == "openai":
                    endpoint = SequenceEndpoint([openai_response([openai_call()])] * 8)
                    client = SimpleNamespace(responses=endpoint)
                    run = providers.run_openai
                else:
                    endpoint = SequenceEndpoint([claude_response([claude_call()], "tool_use")] * 8)
                    client = SimpleNamespace(messages=endpoint)
                    run = providers.run_claude
                with patch.object(providers, "dispatch_tool", return_value=RESULT):
                    with self.assertRaisesRegex(providers.ProviderError, "tool-round limit"):
                        run("dal", client=client)
                self.assertEqual(len(endpoint.calls), providers.MAX_TOOL_ROUNDS + 1)

    def test_missing_keys_fail_before_import_or_network(self):
        with patch.dict(os.environ, {}, clear=True):
            for provider, key in ((providers.run_openai, "OPENAI_API_KEY"), (providers.run_claude, "ANTHROPIC_API_KEY")):
                with self.subTest(key=key):
                    with self.assertRaisesRegex(providers.ProviderError, key):
                        provider("dal")

    def test_empty_prompt_fails_before_client_creation(self):
        for provider in (providers.run_openai, providers.run_claude):
            with self.assertRaisesRegex(providers.ProviderError, "non-empty"):
                provider("  ")

    def test_provider_errors_do_not_echo_sensitive_bodies(self):
        endpoint = SimpleNamespace(create=lambda **kwargs: (_ for _ in ()).throw(ValueError("sensitive body")))
        with self.assertRaises(providers.ProviderError) as raised:
            providers.run_openai("dal", client=SimpleNamespace(responses=endpoint))
        self.assertNotIn("sensitive body", str(raised.exception))


SDK_AVAILABLE = all(importlib.util.find_spec(name) is not None for name in ("openai", "anthropic", "httpx"))


@unittest.skipUnless(SDK_AVAILABLE, "Install .[providers] to run official SDK transport tests")
class OfficialSDKTransportTests(unittest.TestCase):
    """Send realistic JSON through the installed SDKs, with HTTP intercepted."""

    def test_openai_sdk_serializes_state_and_parses_final_text(self):
        import httpx
        from openai import OpenAI

        requests = []
        replies = [
            {"id": "resp_1", "object": "response", "created_at": 1795046400, "status": "completed", "model": providers.DEFAULT_OPENAI_MODEL,
             "output": [{"id": "rs_1", "type": "reasoning", "summary": [], "encrypted_content": "encrypted_state"},
                        {"id": "fc_1", "type": "function_call", "call_id": "call_1", "name": "match_recipes", "arguments": json.dumps(ARGUMENTS), "status": "completed"}]},
            {"id": "resp_2", "object": "response", "created_at": 1795046401, "status": "completed", "model": providers.DEFAULT_OPENAI_MODEL,
             "output": [{"id": "msg_1", "type": "message", "role": "assistant", "status": "completed", "content": [{"type": "output_text", "text": ANSWER, "annotations": []}]}]},
        ]
        def handler(request):
            self.assertEqual(request.url.path, "/v1/responses")
            requests.append(json.loads(request.content))
            return httpx.Response(200, json=replies[len(requests) - 1])
        with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
            client = OpenAI(api_key="test-key-not-real", base_url="https://openai.invalid/v1", http_client=http_client, max_retries=0)
            with patch.object(providers, "dispatch_tool", return_value=RESULT):
                answer = providers.run_openai("dal", client=client)
        self.assertEqual(answer, ANSWER)
        self.assertEqual(requests[1]["input"][1]["encrypted_content"], "encrypted_state")
        self.assertEqual(requests[1]["input"][-1]["call_id"], "call_1")
        self.assertFalse(requests[0]["store"])

    def test_anthropic_sdk_serializes_tool_results_and_thinking(self):
        import httpx
        from anthropic import Anthropic

        requests = []
        replies = [
            {"id": "msg_1", "type": "message", "role": "assistant", "model": providers.DEFAULT_ANTHROPIC_MODEL,
             "stop_reason": "tool_use", "stop_sequence": None, "usage": {"input_tokens": 30, "output_tokens": 20},
             "content": [{"type": "thinking", "thinking": "Check sources", "signature": "opaque_signature"}, claude_call()]},
            {"id": "msg_2", "type": "message", "role": "assistant", "model": providers.DEFAULT_ANTHROPIC_MODEL,
             "stop_reason": "end_turn", "stop_sequence": None, "usage": {"input_tokens": 40, "output_tokens": 20},
             "content": [{"type": "text", "text": ANSWER}]},
        ]
        def handler(request):
            self.assertEqual(request.url.path, "/v1/messages")
            requests.append(json.loads(request.content))
            return httpx.Response(200, json=replies[len(requests) - 1])
        with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
            client = Anthropic(api_key="test-key-not-real", base_url="https://claude.invalid", http_client=http_client, max_retries=0)
            with patch.object(providers, "dispatch_tool", return_value=RESULT):
                answer = providers.run_claude("dal", client=client)
        self.assertEqual(answer, ANSWER)
        self.assertEqual(requests[1]["messages"][-2]["content"][0]["signature"], "opaque_signature")
        self.assertEqual(requests[1]["messages"][-1]["content"][0]["tool_use_id"], "toolu_1")


if __name__ == "__main__":
    unittest.main()
