# Verification record

Recorded November 18, 2026, in the local build environment. These results cover the checked-in demonstration and source snapshot. They do not measure consumer ChatGPT/Claude recommendations or commercial outcomes.

## Observed results

| Check | Result |
| --- | --- |
| Catalog validation | Passed: 14 products, 15 recipe variants; catalog verification date `2026-11-18`. |
| README offline example | Passed: the vegan lentil-dal request returned Dahl Masala, its source recipe, ingredients, method, documented time, and source notes. No AI model was called. |
| Deterministic evaluation | 33/33 reference cases passed. This is a regression check, not an accuracy score for live model answers. |
| Unit and transport suite | 49/49 tests passed, including two tests using the official provider SDKs with mocked HTTP responses and three local key-storage tests. No paid API request was made. |
| Installed wheel | Built and installed in a separate clean virtual environment; catalog validation and all 33 evaluation cases passed without provider SDKs. |
| OpenAI CLI setup error | With `OPENAI_API_KEY` absent, the documented command returned a clear setup message and exit code 2. |
| Claude CLI setup error | With `ANTHROPIC_API_KEY` absent, the documented command returned a clear setup message and exit code 2. |
| OpenAI live attempt | Attempted November 18, 2026. The API returned HTTP 429, `credit_balance_exhausted` / `insufficient_quota`, before generating an answer. Successful live verification remains pending available API credits. |

The local environment used Python 3.9.6, pip 26.0.1, OpenAI SDK 2.48.0, and Anthropic SDK 0.125.0. The project supports environment-variable model overrides; these tests do not establish account access to a selected model.

## Reproduce

After installing the project as shown in the main README:

```bash
python -m moji_demo validate
python -m moji_demo offline --prompt "I want to make vegan lentil dal"
python -m moji_demo evaluate
python -m unittest discover -s tests -v
```

Install `.[providers]` to include the official-SDK transport tests. The supplied GitHub Actions template targets Python 3.9 and 3.12. It has not been installed as an active workflow because the publishing login lacks the `workflow` scope; see [the template](github-actions/checks.yml). This local record does not claim a Python 3.12 execution or a GitHub Actions run.

## Remaining verification

An OpenAI live request was attempted after credentials became available, but the API stopped it for exhausted project credits. No model response, recipe lookup, or completed live case was obtained. The requested default model was `gpt-6.2-sol`; this failed request does not establish access to that model. No credential was saved to this repository. Claude remains untested against the live API because its key is unavailable.

Before a customer-facing release, complete the OpenAI and Claude examples with authorized credentials and available API credits, then review the retrieved records and final claims. Record date, actual model ID, tool arguments, tool results, source accuracy, and usage cost separately from the offline record. Planned smoke cases cover a vegan dal match, refusal to replace an individual spice with a packet, and refusal of an unsupported 30-minute tandoori total.

The Fish Masala cooking recipe remains excluded pending source timing/temperature review. The catalog contains its product record, but the demonstration does not invent a recipe for it. Availability is a dated snapshot, and the demo does not supply live prices or delivery promises.

No official cookbook acceptance, consumer recommendation lift, visits, or sales are established by the checks above. Use the [measurement worksheet](measurement.md) to collect that evidence after distribution.
