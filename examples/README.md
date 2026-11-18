# Provider examples

From the repository root, install the project with `python -m pip install -e '.[providers]'`.
Export the relevant API key in your shell using your usual secret manager; do not commit it.

```sh
python examples/openai_recipe_match.py
python examples/claude_recipe_match.py
```

Both scripts use the same local tool and verified recipe snapshot. They require paid provider API access; a consumer ChatGPT or Claude subscription is not an API key.

The defaults were checked against official documentation on November 18, 2026:

- OpenAI: [`gpt-6.2-sol`](https://developers.openai.com/api/docs/models/gpt-6.2-sol), configurable with `OPENAI_MODEL`.
- Anthropic: [`claude-sonnet-5-5`](https://platform.claude.com/docs/en/models/overview), configurable with `ANTHROPIC_MODEL`.

The OpenAI loop follows the [function calling guide](https://developers.openai.com/api/docs/guides/function-calling): it sends function outputs back with their `call_id` and preserves all returned output, including reasoning items. It uses `store=False` and requests encrypted reasoning for stateless continuation.

The Claude loop follows the [tool result lifecycle](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls): complete assistant content is followed immediately by all tool results. Current Sonnet models reject forced tool selection, so it uses `auto` and refuses to return an answer if the model skips retrieval. See [tool choice restrictions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools).

These examples enforce that a catalog lookup happened and prevent invented source URLs. Prompt instructions constrain factual claims, but do not prove every generated sentence is correct. Review results and run the evaluation set before deploying a customer-facing assistant. Live model outputs and costs vary.
