---
name: apiyi
description: >-
  Call 400+ AI models (GPT, Claude, Gemini, Grok, DeepSeek, Qwen, Kimi, GLM,
  MiniMax, plus image, video, embedding and rerank models) through APIYI's single
  OpenAI-compatible gateway at api.apiyi.com. Use this when the user mentions
  APIYI, API易, api.apiyi.com or an APIYI_API_KEY; wants one API key across
  multiple model vendors; is repointing an OpenAI, Anthropic or Google SDK
  base_url at a relay; or asks about APIYI base URLs, model IDs, token groups
  (分组), pricing, balance (余额), call logs, or gateway error codes.
license: >-
  Proprietary. Reference documentation for the APIYI service, operated by
  APIYI, LLC. Free to read and follow; the service itself requires an account.
compatibility: >-
  Any agent or SDK that can make HTTPS requests. Verified against the official
  OpenAI, Anthropic and Google GenAI SDKs, and against LangChain, the Vercel AI
  SDK, Claude Code, Cline, Cherry Studio and Codex CLI.
metadata:
  vendor: "APIYI, LLC"
  homepage: "https://api.apiyi.com"
  docs: "https://docs.apiyi.com"
  api_key_env: "APIYI_API_KEY"
  openai_base_url: "https://api.apiyi.com/v1"
  anthropic_base_url: "https://api.apiyi.com"
  gemini_base_url: "https://api.apiyi.com"
  gemini_api_version: "v1beta"
  model_list_endpoint: "https://api.apiyi.com/v1/models"
  console_keys: "https://api.apiyi.com/token"
  console_logs: "https://api.apiyi.com/log"
  console_profile: "https://api.apiyi.com/account/profile"
  model_registry: "https://docs.apiyi.com/model-registry.json"
  developer_kit: "https://docs.apiyi.com/developer-kit"
  cli: "npx apiyi@latest"
  source_repo: "github.com/apiyi-com/skills"
  last_reviewed: "2026-09-03"
  openclaw:
    emoji: "🔑"
    primaryEnv: "APIYI_API_KEY"
    requires:
      bins: ["python3"]
---

# APIYI — one key, 400+ models, OpenAI/Anthropic/Google-compatible gateway

APIYI is an AI API gateway. You point an existing SDK's `base_url` at
`api.apiyi.com`, use an APIYI key, and call models from OpenAI, Anthropic,
Google, xAI, DeepSeek, Alibaba, Moonshot, Zhipu, MiniMax and ByteDance through
one account and one balance. No APIYI-specific SDK exists or is needed.

## When to use this skill

Use it when any of these are true:

- The user mentions APIYI, API易, `api.apiyi.com`, or has an `APIYI_API_KEY`.
- The user wants one API key that works across multiple model vendors.
- The user is repointing an OpenAI, Anthropic or Google GenAI SDK at a relay.
- The user asks about APIYI base URLs, model IDs, token groups (分组), balance
  (余额), call logs, billing, or gateway error codes.
- A request through `api.apiyi.com` returned 400/401/404/429/5xx and needs
  diagnosis.

Do **not** use it when the user is calling a vendor's own API directly
(`api.openai.com`, `api.anthropic.com`, `generativelanguage.googleapis.com`)
and has no APIYI key. Nothing here applies to those.

## What APIYI is not

Stating these up front so you do not invent them:

- **No agent self-registration endpoint.** An account is created by a human at
  `https://api.apiyi.com`. There is no API that mints an account or a key for
  an unattended agent. Ask the user for a key.
- **No free auto-routing model.** There is no `auto`, no `auto:free`, no
  zero-cost tier. New accounts do carry a small trial credit, enough for a
  hello-world; beyond that, calls are billed.
- **No cross-vendor fallback fields.** `models`, `route`, `provider` and similar
  routing extensions are not supported. Pick one `model` per request and
  implement fallback in your own code.
- **No fine-tuning, Files API, org management, or billing management APIs.**
- **Not a model host.** APIYI relays to upstream vendors, so upstream content
  policy, rate limits and outages pass straight through.

## Base URL — the single most common integration bug

### Pick the base URL by SDK, not by model

| SDK / wire format | `base_url` | Why |
|---|---|---|
| OpenAI-compatible (OpenAI SDK, LangChain, Vercel AI SDK, most clients) | `https://api.apiyi.com/v1` | The SDK appends `/chat/completions` to whatever you give it, so `/v1` must be present. |
| Anthropic SDK / Claude-native | `https://api.apiyi.com` | The SDK appends `/v1/messages` itself. Adding `/v1` produces `/v1/v1/messages` and a 404. |
| Google GenAI SDK / Gemini-native | `https://api.apiyi.com` with `api_version` set to `v1beta` | The SDK builds `/v1beta/models/...` itself. Using `v1` mismatches the path. |

That reasoning is the durable part. If you remember why each one differs, you
will never have to look up the table again.

Never leave a trailing slash on `base_url` — it produces doubled slashes and a
404.

### Nodes

Same API on every host; pick by network position, not by feature.

| Host | Use for |
|---|---|
| `api.apiyi.com` | Default. Optimised for mainland China. |
| `vip.apiyi.com` | Clients outside mainland China; direct to backend, lowest latency. |
| `b.apiyi.com` | Backup / enterprise. |
| `api-cf.apiyi.com` | Cloudflare CDN. **Text only**, hard ceiling around 100 seconds. Never use it for image, video, or long reasoning calls. |

## Authentication

Model calls use a bearer token:

```http
Authorization: Bearer sk-your-apiyi-key
Content-Type: application/json
```

Keys start with `sk-`. Create and manage them at `https://api.apiyi.com/token`.

Read the key from the environment — the convention across APIYI's own examples
is `APIYI_API_KEY`. Never hardcode a key, never commit one.

**A second, different credential exists.** The account APIs (balance, logs,
token management) use a *system token* obtained from the bottom of
`https://api.apiyi.com/account/profile` by re-entering the account password.
It is passed **bare in the `Authorization` header with no `Bearer` prefix**, and
it carries full account privileges. Do not confuse the two, and do not put a
system token in application code.

### Key setup and self-check

Do this before any other call, and do it in this order:

1. Look for the key in the `APIYI_API_KEY` environment variable. If you are
   running inside OpenClaw, the key the user saved lives at
   `skills.entries.apiyi.apiKey` in `~/.openclaw/openclaw.json` and OpenClaw
   injects it as `APIYI_API_KEY` for you (declared via `metadata.openclaw.primaryEnv`).
2. If there is no key, ask the user for one. They copy it from
   `https://api.apiyi.com/token`. Put it in the environment variable; never write
   it into source, config that gets committed, or a chat transcript.
3. Self-check. Any of these three gives the same status enum:

   - CLI, no install needed (Node 18+): `npx apiyi@latest check`
   - If this skill was installed from `github.com/apiyi-com/skills`, the bundled
     script: `python3 scripts/apiyi.py --check` (prints JSON)
   - Plain curl:

     ```bash
     curl -s -o /dev/null -w "%{http_code}" https://api.apiyi.com/v1/models \
       -H "Authorization: Bearer $APIYI_API_KEY"
     ```

| Status | Meaning | What to tell the user |
|---|---|---|
| `ready` | `/v1/models` returned 200 | Key works. Say how many models are visible and ask what to build. |
| `no_key` | No key found in any location | Ask for a key from `https://api.apiyi.com/token`, then re-check. |
| `invalid_key` | 401 or 403 | Key is wrong, disabled, or exhausted. Ask the user to re-copy it from the console. |
| `network_error` | Timeout, DNS failure, or 5xx | Retry once; if it persists, try `vip.apiyi.com` (outside mainland China) or `b.apiyi.com`. |

A normal `sk-` key **cannot read the balance**, so there is no `no_balance`
status here. A 429 may mean either rate limiting or an empty balance; do not
guess which. Point the user at `https://api.apiyi.com/account/profile` instead.

## Endpoint map

| Path | Method | Wire format |
|---|---|---|
| `/v1/chat/completions` | POST | OpenAI Chat Completions |
| `/v1/responses` | POST | OpenAI Responses |
| `/v1/messages` | POST | Anthropic Messages (base URL is the root domain) |
| `/v1beta/models/{model}:generateContent` | POST | Gemini generateContent |
| `/v1/embeddings` | POST | OpenAI Embeddings |
| `/v1/images/generations` | POST | OpenAI Images |
| `/v1/images/edits` | POST | OpenAI Image edits |
| `/v1/rerank` | POST | Rerank |
| `/v1/models` | GET | List models available to your key |

Video models do **not** use a single unified path. Each vendor family has its
own submit-and-poll paths. Read the model's own documentation page before
integrating video.

## Model IDs — read this before you type a model name

### The naming rule

Model IDs are **case-sensitive** and **dot-versioned**.

The documentation URLs are not the model IDs. Doc page slugs replace dots with
hyphens for URL safety; the actual ID keeps the dots:

| Documentation URL | Actual model ID |
|---|---|
| `/models/qwen3-7-max` | `qwen3.7-max` |
| `/models/glm-5-2` | `glm-5.2` |
| `/models/gpt-5-6-sol` | `gpt-5.6-sol` |
| `/models/gemini-3-6-flash` | `gemini-3.6-flash` |

So it is `gpt-5.4-mini`, **not** `gpt-5-4-mini`. A hyphenated version number is
a different string and will not resolve. Capitalisation matters too —
`MiniMax-M3` is not `minimax-m3`.

### Always confirm the ID at runtime

The catalog changes weekly. Do not hardcode an ID you have not just seen in a
listing.

```bash
curl -s https://api.apiyi.com/v1/models \
  -H "Authorization: Bearer $APIYI_API_KEY" | jq -r '.data[].id'
```

Without a key, use the public model registry. It is generated from the live
pricing data and is the file the documentation site points agents at:

```bash
curl -s https://docs.apiyi.com/model-registry.json | jq -r '.models[].id'
```

Each entry has `id`, `vendor_en`, `category`, `endpoints`, `groups`,
`billing` (`per_token` or `per_call`, USD list prices) and `docs_url`. Check
`schema_version` (currently 1) before parsing; fields are only ever added, never
renamed, within a schema version.

The raw upstream catalog is also public:

```bash
curl -s https://api.apiyi.com/api/pricing
```

Each entry carries `model_name`, `model_ratio`, `enable_groups`,
`supported_endpoint_types` and `pricing_version`. Two cautions:

- Check `pricing_version` before parsing; the schema is versioned and has
  changed.
- `supported_endpoint_types` is a hint, not a contract. Confirm with one real
  call before you build on it.

### Families on the gateway

OpenAI (GPT and o series), Anthropic Claude, Google Gemini, xAI Grok, DeepSeek,
Alibaba Qwen, Moonshot Kimi, Zhipu GLM, MiniMax, ByteDance Seed, plus image,
video, embedding, rerank and moderation models. Roughly 400 in total.

For a hello-world, `gpt-5.4-mini` is a reasonable cheap default — but list the
models first and confirm it is there.

## Recipes

### Chat Completions

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["APIYI_API_KEY"],
    base_url="https://api.apiyi.com/v1",
)

resp = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(resp.choices[0].message.content)
```

```bash
curl https://api.apiyi.com/v1/chat/completions \
  -H "Authorization: Bearer $APIYI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.4-mini","messages":[{"role":"user","content":"Hello!"}]}'
```

On the `gpt-5.x` family: leave `temperature` at its default of 1, use
`max_completion_tokens` instead of `max_tokens`, and do not send `top_p`.

### Responses

```python
resp = client.responses.create(
    model="gpt-5.4-mini",
    input="Summarise this repository in three bullets.",
    reasoning={"effort": "low"},
)
print(resp.output_text)
```

Note the shape difference: Responses nests it as `reasoning.effort`, while Chat
Completions takes a top-level `reasoning_effort`. Some models are
Responses-only; if a model 404s on `/v1/chat/completions`, try `/v1/responses`
before concluding it is unavailable.

### Claude native

```python
import os, anthropic

client = anthropic.Anthropic(
    api_key=os.environ["APIYI_API_KEY"],
    base_url="https://api.apiyi.com",   # root domain, no /v1
)

msg = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### Gemini native

```python
import os
from google import genai

client = genai.Client(
    api_key=os.environ["APIYI_API_KEY"],
    http_options={
        "base_url": "https://api.apiyi.com",
        "api_version": "v1beta",
    },
)

resp = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Hello!",
)
```

### Embeddings

```bash
curl https://api.apiyi.com/v1/embeddings \
  -H "Authorization: Bearer $APIYI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"text-embedding-3-small","input":"hello world"}'
```

### Rerank

```bash
curl https://api.apiyi.com/v1/rerank \
  -H "Authorization: Bearer $APIYI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"bge-reranker-v2-m3","query":"...","documents":["...","..."],"top_n":3}'
```

- Use the returned `index` to map back to your own document objects. Do not
  match on the returned text.
- `return_documents` has no effect on this channel; originals are echoed back
  regardless.
- `relevance_score` is only comparable within a single request. Do not apply a
  fixed threshold across different queries.
- The model name is case-sensitive; getting it wrong returns 503, not 404.

### Images

`/v1/images/generations` and `/v1/images/edits`, OpenAI-shaped. Base64 output
comes back without a `data:` prefix — add one yourself if you are embedding it
in HTML. Input images must be png, jpg or webp; some phone photos are actually
MPO containers with a `.jpg` extension and will be rejected, so re-encode if you
get an invalid-image error.

Image calls are **synchronous and slow**. See the timeout section.

## Multi-turn, caching and server-side state

**Default to client-managed history.** Send the full conversation in the
`messages` array (Chat Completions) or the `input` array (Responses). That is
the only behaviour that is consistent across every model on the gateway.

`previous_response_id` is **model-dependent** here, and the two failure modes
are opposite:

- On the OpenAI Responses path it does not carry conversation context, so
  relying on it silently loses history.
- On some other models it is *required* to chain explicit prompt caching, and
  omitting it means you never get a cache hit.

Probe the behaviour for the specific model you are using rather than assuming
either way. Do not assume a server-side conversation store exists.

## Reasoning and thinking controls

- Chat Completions: top-level `reasoning_effort`.
- Responses: nested `reasoning.effort`.
- Gemini-native: `thinking_level` / `thinking_budget`.

Reasoning tokens bill at the output rate, and higher effort means both higher
cost and much higher latency. Start low.

If you hit a 400 saying function tools cannot be combined with
`reasoning_effort` on `/v1/chat/completions`, either move the call to
`/v1/responses` or drop the effort parameter. This upstream restriction has been
observed to appear and disappear over time — handle the error, do not design
around it in either direction.

## Timeouts, retries, concurrency

| Workload | Client timeout |
|---|---|
| Plain text chat | 60–120 s |
| Reasoning / thinking models | 300–600 s |
| Long-form output | 300 s and up |
| Image generation / editing | 360 s |
| 4K images, multi-reference | 600 s |

Streaming does **not** rescue a slow reasoning call; the first token can take
minutes on its own.

**Disconnecting does not stop the meter.** If your client times out, the
upstream generation still completes and the request is still billed. A timeout
set too low means you paid and got nothing. Err high.

Retry 429 and 5xx with exponential backoff and jitter. Do not retry 400 or 401 —
they will fail identically.

## Errors

Errors come back as JSON with an `error` object containing `message`, `type`
and `code`.

| Status | Typical meaning | What to do |
|---|---|---|
| 400 | Malformed body, bad parameter, wrong endpoint for the model | Read `error.message`; check the base URL and parameter names |
| 401 | Key invalid, expired, or missing the `Bearer` prefix | Re-copy the key from the console |
| 404 | Model ID does not exist, or the base URL has the wrong path | Check the dot-versioned ID; check `/v1` placement |
| 429 | Rate limited, or balance exhausted | Back off; check the balance |
| 5xx | Gateway or upstream failure | Retry with backoff |

`error.message` is returned **once and is not retained server-side**. Log it
verbatim together with the request ID at the moment it happens, or the
information is gone.

## Account, balance and logs

These use the **system token**, bare, with no `Bearer` prefix.

```bash
curl -s https://api.apiyi.com/api/user/self \
  -H "Authorization: your-system-token" -H "Accept: application/json"
```

The response carries `quota` (remaining) and `used_quota`. The conversion is
**500,000 quota units = 1 USD**, so divide by 500000 to get dollars.

Per-call spend, model, latency and error detail: `GET /api/log/self`, same
credential. The console equivalents are `https://api.apiyi.com/log` and
`https://api.apiyi.com/account/profile`.

Account balance is valid for 365 days from the top-up date and resets on the
next top-up.

## Token groups

A *group* (分组) is a channel selected on the token itself. It determines which
models that key can reach, which upstream route serves them, and the billing
multiplier applied. `default` and `svip` are general-purpose; other groups are
scoped to specific model families.

Group names and their multipliers change as channels are added and retired — a
snapshot in this file would be wrong within weeks. Read the current list on the
token page in the console, or from `enable_groups` in the public pricing
endpoint.

If a model 404s or returns "model not found" with a valid key, the usual cause
is that the key's group does not carry that model. Switch the key's group.

## Pricing

Billing is in USD, pay-as-you-go: per-million-tokens for text models,
per-call for many image and video models. Cached input tokens bill at a reduced
rate. Reasoning tokens bill as output.

**Do not quote prices from this file — it contains none deliberately.** Prices,
group multipliers, recharge bonuses and minimum top-up amounts all change, and
the minimum differs by payment channel. Read them live from
`https://docs.apiyi.com/models` or the console pricing page.

## Known gotchas

1. Anthropic SDK with `/v1` in the base URL produces `/v1/v1/messages` and 404.
   Use the root domain.
2. OpenAI SDK *without* `/v1` produces 404. Use `https://api.apiyi.com/v1`.
3. Gemini SDK on `v1` instead of `v1beta` mismatches the path.
4. Trailing slash on `base_url` produces doubled slashes and 404.
5. Hyphenated version in a model ID (`gpt-5-4-mini`) does not resolve. Use dots.
6. `api-cf.apiyi.com` cuts off around 100 seconds — text only.
7. Image base64 has no `data:` prefix.
8. Rerank `return_documents` is a no-op; use `index` to map results back.
9. `temperature` other than 1 on `gpt-5.x` is rejected.
10. A client timeout does not cancel the upstream job, and you are still billed.

## Verification checklist

Before shipping:

- [ ] The model ID came from a live `GET /v1/models` listing, not from memory.
- [ ] The base URL matches the SDK's wire format, with no trailing slash.
- [ ] The key is read from `APIYI_API_KEY`, not hardcoded or committed.
- [ ] The client timeout matches the workload class.
- [ ] `error.message` and the request ID are logged verbatim on failure.
- [ ] 429 and 5xx retry with exponential backoff; 400 and 401 do not retry.
- [ ] Conversation history is sent explicitly rather than assumed server-side.
- [ ] Any price shown to a user was read live, not copied from this file.

## Where to look things up

Every documentation page is also available as raw Markdown by appending `.md`
to its URL. The pages below are the Simplified Chinese versions; insert `/en`
after the domain for English.

- Developer kit overview (skills, CLI, contract, registry): `https://docs.apiyi.com/developer-kit`
- Model registry (machine-readable IDs, endpoints, groups, prices): `https://docs.apiyi.com/model-registry.json`
- Command line, zero install: `npx apiyi@latest check` (source `github.com/apiyi-com/cli`)
- This skill with the self-check script and references: `github.com/apiyi-com/skills`
- Full page index for agents: `https://docs.apiyi.com/llms.txt`
- Everything concatenated: `https://docs.apiyi.com/llms-full.txt`
- Documentation MCP server: `https://docs.apiyi.com/mcp`
- Getting started: `https://docs.apiyi.com/getting-started`
- API manual: `https://docs.apiyi.com/api-manual`
- Base URL guide: `https://docs.apiyi.com/faq/base-url-config`
- Model list and pricing: `https://docs.apiyi.com/models`
- Console (keys, logs, balance): `https://api.apiyi.com/token`

## Freshness

Last reviewed 2026-09-03. Every model ID, price, group name and quota figure on
this gateway is volatile; this file deliberately states conventions and
mechanisms rather than quoting them. If you find a number here that is not the
quota conversion (500,000 = 1 USD), the balance validity period (365 days), or a
timeout recommendation, treat it as a bug and look it up live instead.
