# Troubleshooting

Every response from `scripts/apiyi.py` is JSON with a `status` field, and the
process exit code mirrors it.

| exit | status | meaning | fix |
|---|---|---|---|
| 0 | `ok` / `ready` | success | |
| 2 | `no_key` | no key in flag, env, config or openclaw.json | ask the user for a key, see api-key-setup.md |
| 3 | `invalid_key` | 401 / 403 | re-copy the key from https://api.apiyi.com/token |
| 4 | `network_error` | DNS, timeout, or 5xx | retry once, then `--node vip` or `--node b` |
| 5 | `model_not_found` | 404 | check the ID against the registry (dots, case); or the key's group lacks the model |
| 6 | `rate_limited_or_no_balance` | 429 | back off; if it persists, the balance may be empty, send the user to the console |
| 7 | `bad_request` | 400 | read `hint` (the upstream `error.message`); usually a parameter the model does not accept |
| 8 | `bad_args` | command line misuse | see `--help` |
| 1 | `unexpected` | anything else | include `hint` when reporting |

Common 400s: `temperature` other than 1 on `gpt-5.x`; `max_tokens` on models that
want `max_completion_tokens`; tools combined with `reasoning_effort` on
`/v1/chat/completions` (move to `/v1/responses`).

`error.message` is returned once and not stored server-side. Log it verbatim
with the request ID at the moment it happens.
