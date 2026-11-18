# API setup for the live examples

API keys are needed only for real provider requests. Offline matching, catalog validation, and the simulated SDK tests work without them.

1. Create a project API key in the [OpenAI API dashboard](https://platform.openai.com/api-keys). Name it `Moji demo` so you can identify it later. See the [official quickstart](https://developers.openai.com/api/docs/quickstart).
2. Create a development API key in the [Claude Console](https://platform.claude.com/settings/keys), scoped to the appropriate workspace. See the [official key instructions](https://platform.claude.com/docs/en/get-api-key). The example needs the regular Claude API, not an administrative key.
3. Configure API billing or credits if your account requires it. API use may be billed separately from a chat subscription; [OpenAI billing details](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform).

For an assisted local setup, run this in Terminal from the repository root:

```bash
python3 scripts/configure_api_keys.py
```

Paste each key at its hidden prompt. Press Enter to skip a provider. This makes no API calls and saves `.env.local` with owner-only permissions. Git ignores the file; the helper refuses to replace an existing file. In an assisted Codex session, report only that the file was saved, or share its path. Never put a key in chat, a screenshot, or a commit.

The examples read environment variables; they do not automatically execute or load `.env.local`. For standalone use, set `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` using your preferred secret manager as described in the main README. Do not execute an untrusted configuration file as a shell script. The local helper is an optional handoff mechanism, not a hosted secret store.
