#!/usr/bin/env python3
"""Protocol fixture checks; TTFT is a low-load diagnostic, not a load benchmark."""
import json
import time
import urllib.error
import urllib.request

CASES = {
    "openai": {"path": "/v1/chat/completions", "model": "bench-openai", "praxis_port": 28082},
    "anthropic": {"path": "/v1/messages", "model": "bench-anthropic", "praxis_port": 28083},
    "translation": {"path": "/v1/messages", "model": "bench-openai", "praxis_port": 28084},
}


def payload(case, size=1024, stream=False):
    value = {"model": CASES[case]["model"], "messages": [{"role": "user", "content": "a" * size}], "max_tokens": 64, "stream": stream}
    if case == "openai" and stream:
        value["stream_options"] = {"include_usage": True}
    return json.dumps(value, separators=(",", ":")).encode()


def endpoint(gateway, case, container=False):
    if container:
        host = {"agentgateway": "agentgateway:8080", "praxis": "praxis:" + str({"openai": 8080, "anthropic": 8082, "translation": 8084}[case]), "direct": "mock:8081"}[gateway]
    else:
        host = "127.0.0.1:" + str({"agentgateway": 28080, "praxis": CASES[case]["praxis_port"], "direct": 28081}[gateway])
    # Direct baseline for translation exercises the upstream Chat Completions API.
    path = "/v1/chat/completions" if gateway == "direct" and case == "translation" else CASES[case]["path"]
    return "http://" + host + path


def probe(gateway, case, stream=False, error=False, size=1024):
    headers = {"Content-Type": "application/json", "Authorization": "Bearer dummy", "x-api-key": "dummy", "anthropic-version": "2023-06-01", "x-bench-output-bytes": str(size)}
    if error:
        headers["x-bench-error"] = "true"
    native_case = "openai" if gateway == "direct" and case == "translation" else case
    req = urllib.request.Request(endpoint(gateway,case), data=payload(native_case, size=size, stream=stream), headers=headers)
    started = time.monotonic()
    text, first, events, final, usage = "", None, 0, False, None
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            status = resp.status
            assert not error, "upstream error was converted to success"
            if stream:
                assert "text/event-stream" in resp.headers.get("Content-Type", "")
                for raw in resp:
                    line = raw.decode().strip()
                    if not line.startswith("data:"):
                        continue
                    raw_value = line[5:].strip()
                    if raw_value == "[DONE]":
                        final = True
                        continue
                    value = json.loads(raw_value)
                    events += 1
                    piece = ""
                    if value.get("choices"):
                        piece = value["choices"][0].get("delta", {}).get("content") or ""
                    elif value.get("type") == "content_block_delta":
                        piece = value.get("delta", {}).get("text", "")
                    if piece:
                        if first is None:
                            first = time.monotonic() - started
                        text += piece
                    if value.get("type") == "message_stop":
                        final = True
                    if value.get("usage"):
                        usage = value["usage"]
                assert final, "missing terminal SSE event"
            else:
                value = json.load(resp)
                if native_case == "openai":
                    text = value["choices"][0]["message"]["content"]
                    assert value["usage"]["total_tokens"] == 192
                else:
                    text = "".join(c.get("text", "") for c in value["content"])
                    assert value["usage"]["input_tokens"] == 128
                    assert value["usage"]["output_tokens"] == 64
                usage = value["usage"]
            assert text == "x"*size, f"content mismatch: {len(text)} bytes"
    except urllib.error.HTTPError as exc:
        if not error or exc.code != 429:
            raise
        status = exc.code
        json.loads(exc.read())
    elapsed = time.monotonic() - started
    if stream:
        assert usage is not None, "missing stream usage"
        assert first < elapsed / 2, "stream appears buffered until completion"
    return {"gateway":gateway,"case":case,"stream":stream,"upstream_error":error,"requested_bytes":size,"status":status,"content_bytes":len(text),"events":events,"usage":usage,"first_content_seconds":first,"elapsed_seconds":elapsed,"passed":True}


if __name__ == "__main__":
    for gateway in ("direct", "agentgateway", "praxis"):
        for case in CASES:
            for stream, error in ((False,False),(True,False),(False,True)):
                print(json.dumps(probe(gateway,case,stream,error)), flush=True)
