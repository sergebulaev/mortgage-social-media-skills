#!/usr/bin/env python3
"""A fake Publora MCP server (personal tools) for the behaviour evals.

Stdio JSON-RPC, no dependencies. Answers from a scenario file and appends every
call to a JSONL log, so a grader can see exactly what the agent did. It never
talks to Publora.

    MOCK_SCENARIO=<scenario.json> MOCK_LOG=<calls.jsonl> python3 mock_publora_mcp.py
"""
from __future__ import annotations

import json
import os
import sys
import uuid

SCEN = json.load(open(os.environ["MOCK_SCENARIO"], encoding="utf-8")) if os.environ.get("MOCK_SCENARIO") else {}
LOG = os.environ.get("MOCK_LOG", os.devnull)
POSTS: dict = {}


def log(name, args):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({"tool": name, "args": args}, ensure_ascii=False) + "\n")


def oid():
    return uuid.uuid4().hex[:24]


def account_context(_):
    return {"success": True, "plan": "pro", "features": {"scheduling": True, "drafts": True},
            "scheduleHorizonDays": 365, "allowedPlatforms": ["facebook", "instagram", "linkedin", "twitter",
                                                            "threads", "bluesky", "tiktok", "youtube"]}


def list_connections(_):
    return {"success": True, "connections": SCEN.get("connections", [
        {"platformId": "facebook-90000000001", "username": "Test Business", "tokenStatus": "valid"},
        {"platformId": "instagram-90000000002", "username": "testbusiness", "tokenStatus": "valid"},
        {"platformId": "linkedin-90000000003", "username": "Test Owner", "tokenStatus": "valid"}])}


def create_post(args):
    pg = oid()
    status = "scheduled" if (args.get("scheduledTime") or args.get("publishNow")) else "draft"
    POSTS[pg] = {**args, "status": status}
    return {"success": True, "postGroupId": pg, "scheduledTime": args.get("scheduledTime"), "status": status}


def update_post(args):
    pg = args.get("postGroupId")
    POSTS.setdefault(pg, {}).update(args)
    return {"success": True, "postGroupId": pg}


def get_post(args):
    pg = args.get("postGroupId")
    return {"success": True, "postGroup": {"id": pg, **POSTS.get(pg, {"status": "draft"})}}


def list_posts(_):
    return {"success": True, "posts": [{"postGroupId": k, **v} for k, v in POSTS.items()]}


def ok(_):
    return {"success": True}


TOOLS = {
    "account_context": (account_context, {}),
    "list_connections": (list_connections, {}),
    "create_post": (create_post, {"content": {"type": "string"}, "platforms": {"type": "array", "items": {"type": "string"}},
                                  "scheduledTime": {"type": "string"}, "publishNow": {"type": "boolean"},
                                  "mediaUrls": {"type": "array", "items": {"type": "string"}},
                                  "platformSettings": {"type": "object"}, "idempotencyKey": {"type": "string"},
                                  "firstComments": {"type": "array"}}),
    "update_post": (update_post, {"postGroupId": {"type": "string"}, "content": {"type": "string"},
                                  "status": {"type": "string"}, "scheduledTime": {"type": "string"},
                                  "publishNow": {"type": "boolean"}, "platforms": {"type": "array"},
                                  "mediaUrls": {"type": "array"}, "platformSettings": {"type": "object"}}),
    "get_post": (get_post, {"postGroupId": {"type": "string"}}),
    "list_posts": (list_posts, {}),
    "delete_post": (ok, {"postGroupId": {"type": "string"}}),
}
DESCRIPTIONS = {
    "create_post": "Create a post. Omit scheduledTime (and publishNow) to create a DRAFT. publishNow=true publishes immediately.",
    "update_post": "Edit a draft or scheduled post: content, status (draft|scheduled), scheduledTime, publishNow.",
}


def respond(rid, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": rid}
    msg["error" if error else "result"] = error or result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        try:
            req = json.loads(line)
        except ValueError:
            continue
        method, rid = req.get("method"), req.get("id")
        if method == "initialize":
            respond(rid, {"protocolVersion": req.get("params", {}).get("protocolVersion", "2024-11-05"),
                          "capabilities": {"tools": {}}, "serverInfo": {"name": "publora", "version": "eval"}})
        elif method == "tools/list":
            respond(rid, {"tools": [{"name": n, "description": DESCRIPTIONS.get(n, n.replace("_", " ")),
                                     "inputSchema": {"type": "object", "properties": props}}
                                    for n, (_, props) in TOOLS.items()]})
        elif method == "tools/call":
            name = req["params"]["name"]
            args = req["params"].get("arguments") or {}
            log(name, args)
            fn = TOOLS.get(name, (None,))[0]
            out = fn(args) if fn else {"success": False, "error": f"unknown tool {name}"}
            respond(rid, {"content": [{"type": "text", "text": json.dumps(out)}]})
        elif rid is not None:
            respond(rid, {})


if __name__ == "__main__":
    main()
