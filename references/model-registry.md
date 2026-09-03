# Model registry

`https://docs.apiyi.com/model-registry.json` is the machine-readable source of
truth for model IDs. It is regenerated from live pricing data whenever the
documentation's pricing table is rebuilt.

```bash
curl -s https://docs.apiyi.com/model-registry.json | jq -r '.models[].id'
python3 {baseDir}/scripts/apiyi.py --models --grep gpt-5
```

## Shape

Top level: `schema_version` (currently 1; fields are only added within a
version), `generated_at`, `base_urls`, `nodes`, `endpoints`, `groups`,
`model_count`, `models[]`.

Each model:

| field | meaning |
|---|---|
| `id` | Use verbatim. Case-sensitive, dot-versioned (`gpt-5.4-mini`, `MiniMax-M3`). |
| `vendor_en` | Vendor name. |
| `category` | `text`, `image`, `video`, `embedding`, ... |
| `endpoints` | Which endpoint names this model accepts; look each up in the top-level `endpoints` map for the path. |
| `groups` | Token groups that can reach it. If a valid key gets "model not found", the key's group usually lacks the model. |
| `billing.type` | `per_token` (USD per million tokens) or `per_call`. |
| `billing.*_usd_per_m`, `billing.per_call_usd` | List prices before discounts. Never quote them as final; the console is authoritative. |
| `docs_url` | Detail page when one exists. |

## Rules

- Documentation URLs are not model IDs. `/models/qwen3-7-max` is the page for `qwen3.7-max`.
- With a key, prefer `GET /v1/models`: it lists exactly what that key's group can reach.
- Pick the endpoint by the model's `endpoints`, and the base URL by the SDK you are using (see SKILL.md).
