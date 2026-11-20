# Verification record

Initial offline checks recorded November 18, 2026; updated local checks and both providers' live checks recorded November 19, 2026. These results cover the checked-in demonstration and source snapshot. They do not measure consumer ChatGPT/Claude recommendations or commercial outcomes.

## Observed results

| Check | Result |
| --- | --- |
| Catalog validation | Passed: 14 products, 15 recipe variants; catalog verification date `2026-11-18`. |
| README offline example | Passed: the vegan lentil-dal request returned Dahl Masala, its source recipe, ingredients, method, documented time, and source notes. No AI model was called. |
| Deterministic evaluation | 33/33 reference cases passed. This is a regression check, not an accuracy score for live model answers. |
| Unit and transport suite | 55/55 tests passed, including two tests using the official provider SDKs with mocked HTTP responses and nine local key-storage tests. This suite makes no paid API requests. |
| Installed wheel | Built and installed in a separate clean virtual environment; catalog validation and all 33 evaluation cases passed without provider SDKs. |
| OpenAI CLI setup error | With `OPENAI_API_KEY` absent, the documented command returned a clear setup message and exit code 2. |
| Claude CLI setup error | With `ANTHROPIC_API_KEY` absent, the documented command returned a clear setup message and exit code 2. |
| OpenAI live API | Passed November 19, 2026: all three end-to-end smoke cases, using six real requests served by `gpt-6.2-sol`. The prior November 18 credit-balance error was resolved after credits were added. See [live results](live-verification.md). |
| Claude live API | Passed November 19, 2026: all three end-to-end smoke cases, using six real requests served by `claude-sonnet-5-5`. A focused two-request follow-up confirmed that unknown elapsed times are not promised as available in a future answer. See [live results](live-verification.md). |

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

Both providers' smoke checks have completed successfully. Credentials remain in hidden process input or ignored local configuration and were not committed to Git or included in results. The key-entry helper now handles an exact accidental double paste without changing other input or replacing existing files.

Before a customer-facing release, expand model-level evaluation beyond these three smoke cases and continue reviewing source facts and generated claims. Record date, actual model ID, tool arguments, tool results, source accuracy, and usage cost separately from the offline record. These results do not prove every possible cooking request will be handled correctly.

The Fish Masala cooking recipe remains excluded pending source timing/temperature review. The catalog contains its product record, but the demonstration does not invent a recipe for it. Availability is a dated snapshot, and the demo does not supply live prices or delivery promises.

No official cookbook acceptance, consumer recommendation lift, visits, or sales are established by the checks above. Use the [measurement worksheet](measurement.md) to collect that evidence after distribution.
