# API key setup

Run the self-check first and react to its `status`:

```bash
python3 {baseDir}/scripts/apiyi.py --check
```

| status | Say to the user | Then |
|---|---|---|
| `ready` | "Key works. I can see N models. What would you like to build?" | Proceed. |
| `no_key` | "I need an APIYI key. Copy one at https://api.apiyi.com/token and paste it here." | Save it (below), re-check. |
| `invalid_key` | "That key was rejected (401/403). Please re-copy it from https://api.apiyi.com/token; keys start with sk-." | Re-check with the new key. |
| `network_error` | "I cannot reach api.apiyi.com right now." | Retry once; then try `--node vip` (outside mainland China) or `--node b`. |

## Where the key lives

1. Environment variable `APIYI_API_KEY` (preferred everywhere).
2. OpenClaw: `~/.openclaw/openclaw.json` under `skills.entries.apiyi.apiKey`.
   OpenClaw injects it as `APIYI_API_KEY` at run time because this skill declares
   `metadata.openclaw.primaryEnv: APIYI_API_KEY`.
3. The APIYI CLI: `~/.config/apiyi/config.json` (`{"apiKey": "sk-..."}`), written by
   `npx apiyi@latest auth set-key` with mode 0600.

The script checks all of these in that order, so a key saved by any one tool is
found by the others.

## Saving a key the user pasted (OpenClaw)

Verify it first, then persist:

```bash
python3 {baseDir}/scripts/apiyi.py --check --api-key THE_KEY
python3 - <<'PY'
import json, pathlib
p = pathlib.Path.home() / ".openclaw" / "openclaw.json"
cfg = json.loads(p.read_text()) if p.exists() else {}
cfg.setdefault("skills", {}).setdefault("entries", {}).setdefault("apiyi", {})["apiKey"] = "THE_KEY"
p.write_text(json.dumps(cfg, indent=2))
PY
```

Replace `THE_KEY` with the real key. Never echo the full key back into the chat; show at most the first 6 and last 4 characters.

## What a normal key cannot do

An `sk-` key can call models but **cannot read the balance**. Balance, logs and
token management use a separate system token (from the bottom of
https://api.apiyi.com/account/profile, passed bare with no `Bearer` prefix).
So there is no `no_balance` status. If a call returns 429, tell the user it is
either rate limiting or an empty balance and point them at
https://api.apiyi.com/account/profile rather than guessing.
