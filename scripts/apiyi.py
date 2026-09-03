#!/usr/bin/env python3
"""APIYI skill helper. Python 3.8+, standard library only.

  python3 apiyi.py --check                     # key / node self-check, prints JSON
  python3 apiyi.py --models [--grep gpt-5]     # list model IDs (uses public registry when no key)
  python3 apiyi.py --chat "Hello" [-m gpt-5.4-mini]

Key lookup order: --api-key, APIYI_API_KEY, ~/.config/apiyi/config.json,
~/.openclaw/openclaw.json (skills.entries.apiyi.apiKey).

Exit codes: 0 ok, 2 no_key, 3 invalid_key, 4 network_error, 5 model_not_found,
6 rate_limited_or_no_balance, 7 bad_request, 8 bad_args, 1 unexpected.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

NODES = {
    "api": "https://api.apiyi.com",
    "vip": "https://vip.apiyi.com",
    "b": "https://b.apiyi.com",
    "cf": "https://api-cf.apiyi.com",
}
REGISTRY_URL = "https://docs.apiyi.com/model-registry.json"
PRICING_URL = "https://api.apiyi.com/api/pricing"
DEFAULT_MODEL = "gpt-5.4-mini"
UA = "apiyi-skill/1.0"

EXIT = {
    "ok": 0, "unexpected": 1, "no_key": 2, "invalid_key": 3, "network_error": 4,
    "model_not_found": 5, "rate_limited_or_no_balance": 6, "bad_request": 7, "bad_args": 8,
}


def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def resolve_key(explicit=None):
    """Return (key, source) or (None, None)."""
    if explicit:
        return explicit.strip(), "--api-key"
    env = os.environ.get("APIYI_API_KEY", "").strip()
    if env:
        return env, "APIYI_API_KEY"
    cfg = _read_json(Path.home() / ".config" / "apiyi" / "config.json")
    if cfg and cfg.get("apiKey"):
        return str(cfg["apiKey"]).strip(), "~/.config/apiyi/config.json"
    oc = _read_json(Path.home() / ".openclaw" / "openclaw.json")
    try:
        k = oc["skills"]["entries"]["apiyi"]["apiKey"]
        if k:
            return str(k).strip(), "~/.openclaw/openclaw.json"
    except (KeyError, TypeError):
        pass
    return None, None


def key_shape_problem(key):
    """Return a human-readable problem with the key's shape, or None."""
    if not key:
        return None
    if any(not (0x21 <= ord(c) <= 0x7E) for c in key):
        return "contains non-ASCII or whitespace characters (is it a placeholder like <YOUR_KEY>?)"
    if not key.startswith("sk-"):
        return 'does not start with "sk-"'
    return None


def request(method, url, key=None, body=None, timeout=30):
    headers = {"Accept": "application/json", "User-Agent": UA}
    if key:
        headers["Authorization"] = "Bearer " + key
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, raw, int((time.monotonic() - t0) * 1000)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        return e.code, raw, int((time.monotonic() - t0) * 1000)


def classify_http(status):
    if status in (401, 403):
        return "invalid_key"
    if status == 404:
        return "model_not_found"
    if status == 429:
        return "rate_limited_or_no_balance"
    if status == 400:
        return "bad_request"
    if status >= 500:
        return "network_error"
    return "unexpected"


def error_message(raw):
    try:
        j = json.loads(raw)
        return (j.get("error") or {}).get("message") or j.get("message") or raw[:300]
    except ValueError:
        return raw[:300]


def cmd_check(args):
    key, source = resolve_key(args.api_key)
    base = NODES[args.node]
    out = {"status": None, "node": base.replace("https://", ""), "key_source": source,
           "model_count": None, "latency_ms": None}
    if not key:
        out["status"] = "no_key"
        out["hint"] = "Copy a key at https://api.apiyi.com/token and export APIYI_API_KEY"
        return out
    problem = key_shape_problem(key)
    if problem:
        out["status"] = "invalid_key"
        out["hint"] = "The key from %s %s. Copy a real one at https://api.apiyi.com/token" % (source, problem)
        return out
    try:
        status, raw, ms = request("GET", base + "/v1/models", key, timeout=args.timeout)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        out["status"] = "network_error"
        out["hint"] = str(e)
        return out
    out["latency_ms"] = ms
    if status == 200:
        try:
            out["model_count"] = len(json.loads(raw).get("data", []))
        except ValueError:
            pass
        out["status"] = "ready"
    else:
        out["status"] = classify_http(status)
        if out["status"] not in ("invalid_key", "network_error"):
            out["status"] = "unexpected"
        out["http_status"] = status
        out["hint"] = error_message(raw)
    return out


def cmd_models(args):
    key, _ = resolve_key(args.api_key)
    ids = []
    if key:
        status, raw, _ = request("GET", NODES[args.node] + "/v1/models", key, timeout=args.timeout)
        if status != 200:
            return {"status": classify_http(status), "http_status": status, "hint": error_message(raw)}
        ids = [m["id"] for m in json.loads(raw).get("data", [])]
        source = "/v1/models"
    else:
        try:
            status, raw, _ = request("GET", REGISTRY_URL, timeout=args.timeout)
            reg = json.loads(raw)
            ids = [m["id"] for m in reg.get("models", [])]
            source = REGISTRY_URL
        except Exception:
            status, raw, _ = request("GET", PRICING_URL, timeout=args.timeout)
            ids = [m["model_name"] for m in json.loads(raw).get("data", [])]
            source = PRICING_URL
    if args.grep:
        g = args.grep.lower()
        ids = [i for i in ids if g in i.lower()]
    return {"status": "ok", "source": source, "count": len(ids), "models": sorted(ids)}


def cmd_chat(args):
    key, _ = resolve_key(args.api_key)
    if not key:
        return {"status": "no_key", "hint": "Copy a key at https://api.apiyi.com/token and export APIYI_API_KEY"}
    problem = key_shape_problem(key)
    if problem:
        return {"status": "invalid_key", "hint": "The API key %s. Copy a real one at https://api.apiyi.com/token" % problem}
    body = {"model": args.model, "messages": [{"role": "user", "content": args.chat}]}
    try:
        status, raw, ms = request("POST", NODES[args.node] + "/v1/chat/completions", key, body, timeout=args.timeout)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {"status": "network_error", "hint": str(e)}
    if status != 200:
        return {"status": classify_http(status), "http_status": status, "model": args.model, "hint": error_message(raw)}
    j = json.loads(raw)
    content = ((j.get("choices") or [{}])[0].get("message") or {}).get("content")
    return {"status": "ok", "model": j.get("model", args.model), "latency_ms": ms,
            "content": content, "usage": j.get("usage")}


def main(argv=None):
    p = argparse.ArgumentParser(description="APIYI skill helper (stdlib only)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="self-check key and node")
    g.add_argument("--models", action="store_true", help="list model IDs")
    g.add_argument("--chat", metavar="PROMPT", help="send one chat message")
    p.add_argument("-m", "--model", default=DEFAULT_MODEL)
    p.add_argument("--grep", help="filter model IDs (case-insensitive substring)")
    p.add_argument("--api-key", help="override key lookup")
    p.add_argument("--node", choices=list(NODES), default="api")
    p.add_argument("--timeout", type=int, default=30)
    try:
        args = p.parse_args(argv)
    except SystemExit:
        return EXIT["bad_args"]

    try:
        if args.check:
            out = cmd_check(args)
        elif args.models:
            out = cmd_models(args)
        else:
            out = cmd_chat(args)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        out = {"status": "network_error", "hint": str(e)}
    except Exception as e:  # noqa: BLE001
        out = {"status": "unexpected", "hint": repr(e)}

    print(json.dumps(out, ensure_ascii=False, indent=2))
    st = out.get("status")
    if st in ("ok", "ready"):
        return 0
    return EXIT.get(st, 1)


if __name__ == "__main__":
    sys.exit(main())
