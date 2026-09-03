# APIYI skill

An [Agent Skills](https://agentskills.io) package that teaches a chat or coding
agent how to call 400+ models (GPT, Claude, Gemini, Grok, DeepSeek, Qwen, Kimi,
GLM, MiniMax, image, video, embedding and rerank models) through APIYI's
OpenAI / Anthropic / Google compatible gateway at `api.apiyi.com`.

`SKILL.md` is a byte-identical copy of https://docs.apiyi.com/skill.md, which
the documentation site also exposes through `/.well-known/agent-skills`. This
repository adds a self-check script and reference notes so that OpenClaw and
other git-installing agents get the scripted version.

## Install

Paste one of these to your agent:

```
从 https://docs.apiyi.com 安装 API易（APIYI）技能，并引导我配置 API Key。
```

```
Install the APIYI skill from https://github.com/apiyi/skills and guide me to configure an API key.
```

Or do it yourself:

| Agent | Command |
|---|---|
| Claude Code, Cursor, Codex and other Agent Skills tools | `npx skills add https://docs.apiyi.com` (or `npx skills add apiyi/skills`) |
| OpenClaw | `openclaw skills install git:apiyi/skills` or `git clone https://github.com/apiyi/skills ~/.openclaw/workspace/skills/apiyi` |
| Anything else | copy `SKILL.md` into the agent's skills directory |

## Self-check

```bash
python3 scripts/apiyi.py --check
python3 scripts/apiyi.py --models --grep gpt-5
python3 scripts/apiyi.py --chat "Hello" -m gpt-5.4-mini
```

Python 3.8+, standard library only. Exit codes and statuses are listed in
`references/troubleshooting.md`. There is also a Node CLI with more commands:
`npx apiyi@latest check` (source: https://github.com/apiyi/cli).

## Layout

```
SKILL.md                      the skill (synced from docs.apiyi.com/skill.md)
scripts/apiyi.py              --check / --models / --chat
references/api-key-setup.md   how to ask for, verify and store a key
references/model-registry.md  how to read docs.apiyi.com/model-registry.json
references/troubleshooting.md status and exit code table
```

## Links

- Developer kit overview: https://docs.apiyi.com/developer-kit
- Model registry: https://docs.apiyi.com/model-registry.json
- Console (keys, logs, balance): https://api.apiyi.com/token

## License

MIT for the scripts and reference notes in this repository. `SKILL.md` is
reference documentation for the APIYI service; see its frontmatter.
