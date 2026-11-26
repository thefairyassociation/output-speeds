"""Output-speed benchmark for current Claude and OpenAI models across effort levels.

Per run we stream one response and record:
  ttft_s       time from request to first *visible* text delta (includes any reasoning)
  out_tok_s    visible-output decode speed: visible tokens / (last delta - first delta)
  out_char_s   same, in characters/s (tokenizer-neutral, comparable across providers)
  e2e_tok_s    all generated tokens (reasoning + visible) / total wall time
  reasoning    reasoning/thinking tokens (OpenAI reports these; for Claude it is
               output_tokens minus counted visible tokens)

Usage: python bench.py [--runs N] [--fast] [--only anthropic|openai] [--out results.jsonl]
"""

import argparse
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

PROMPT = (
    "Explain how TCP congestion control works, covering slow start, congestion "
    "avoidance, fast retransmit/recovery, and how CUBIC and BBR differ. "
    "Write roughly 700 words of plain prose (no tables, no code)."
)
EFFORTS = ["low", "medium", "high", "xhigh"]
MAX_TOKENS = 32000
FAST = False  # set by --fast
CLAUDE_FAST_MODELS = {"claude-opus-5-5"}  # fast mode is Opus 5.5 only

CLAUDE_MODELS = ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"]
OPENAI_MODELS = ["gpt-6.2-astra", "gpt-6.2-sol", "gpt-6.1-terra", "gpt-6-luna"]


def anthropic_key():
    return os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("BENCH_ANTHROPIC_API_KEY")


def run_claude(client, model, effort):
    t0 = time.perf_counter()
    first = last = None
    text = []
    with client.messages.stream(
        model=model,
        max_tokens=MAX_TOKENS,
        thinking={"type": "adaptive"},
        output_config={"effort": effort},
        messages=[{"role": "user", "content": PROMPT}],
        **({"speed": "fast"} if FAST else {}),
    ) as stream:
        for ev in stream:
            if ev.type == "content_block_delta" and ev.delta.type == "text_delta":
                now = time.perf_counter()
                first = first or now
                last = now
                text.append(ev.delta.text)
        msg = stream.get_final_message()
    t_end = time.perf_counter()
    body = "".join(text)
    # Visible-token count via count_tokens (difference removes the message framing overhead).
    base = client.messages.count_tokens(model=model, messages=[{"role": "user", "content": "x"}]).input_tokens
    full = client.messages.count_tokens(model=model, messages=[{"role": "user", "content": "x" + body}]).input_tokens
    visible = max(full - base, 1)
    total_out = msg.usage.output_tokens
    return dict(
        stop=msg.stop_reason, t0=t0, first=first, last=last, end=t_end,
        visible_tokens=visible, total_out=total_out,
        reasoning=max(total_out - visible, 0), chars=len(body),
        tier=getattr(msg.usage, "speed", None) or "standard",
    )


def run_openai(client, model, effort):
    t0 = time.perf_counter()
    first = last = None
    text = []
    final = None
    stream = client.responses.create(
        model=model, input=PROMPT, reasoning={"effort": effort},
        max_output_tokens=MAX_TOKENS, stream=True,
        **({"service_tier": "fast"} if FAST else {}),
    )
    for ev in stream:
        if ev.type == "response.output_text.delta":
            now = time.perf_counter()
            first = first or now
            last = now
            text.append(ev.delta)
        elif ev.type in ("response.completed", "response.incomplete"):
            final = ev.response
    t_end = time.perf_counter()
    u = final.usage
    reasoning = u.output_tokens_details.reasoning_tokens or 0
    return dict(
        stop=final.status, t0=t0, first=first, last=last, end=t_end,
        visible_tokens=u.output_tokens - reasoning, total_out=u.output_tokens,
        reasoning=reasoning, chars=len("".join(text)),
        tier=final.service_tier,
    )


def metrics(r):
    span = (r["last"] - r["first"]) if r["first"] else 0
    total = r["end"] - r["t0"]
    return dict(
        ttft_s=round((r["first"] or r["end"]) - r["t0"], 3),
        total_s=round(total, 3),
        out_tok_s=round(r["visible_tokens"] / span, 1) if span > 0.05 else None,
        out_char_s=round(r["chars"] / span, 1) if span > 0.05 else None,
        e2e_tok_s=round(r["total_out"] / total, 1),
        visible_tokens=r["visible_tokens"], reasoning_tokens=r["reasoning"],
        total_out=r["total_out"], chars=r["chars"], stop=r["stop"], tier=r["tier"],
    )


def bench_model(provider, model, runs, out_path):
    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=anthropic_key(), base_url="https://api.anthropic.com")
        fn = run_claude
    else:
        import openai
        client = openai.OpenAI()
        fn = run_openai
    rows = []
    for effort in EFFORTS:
        for i in range(runs):
            try:
                m = metrics(fn(client, model, effort))
            except Exception as ex:  # record and keep going
                m = dict(error=f"{type(ex).__name__}: {str(ex)[:300]}")
            row = dict(provider=provider, model=model, effort=effort, run=i, **m)
            rows.append(row)
            with open(out_path, "a") as f:
                f.write(json.dumps(row) + "\n")
            print(json.dumps(row), flush=True)
    return rows


def summarize(rows):
    def med(xs):
        xs = [x for x in xs if x is not None]
        return round(statistics.median(xs), 1) if xs else None

    groups = {}
    for r in rows:
        if "error" in r:
            continue
        groups.setdefault((r["model"], r["effort"]), []).append(r)
    hdr = f"{'model':<20}{'effort':<8}{'n':>3}{'out tok/s':>11}{'chars/s':>9}{'TTFT s':>8}{'total s':>9}{'reason tok':>11}{'vis tok':>9}{'e2e tok/s':>11}"
    print(hdr)
    print("-" * len(hdr))
    for (model, effort), g in groups.items():
        print(f"{model:<20}{effort:<8}{len(g):>3}"
              f"{med([x['out_tok_s'] for x in g]) or '-':>11}"
              f"{med([x['out_char_s'] for x in g]) or '-':>9}"
              f"{med([x['ttft_s'] for x in g]):>8}"
              f"{med([x['total_s'] for x in g]):>9}"
              f"{med([x['reasoning_tokens'] for x in g]):>11}"
              f"{med([x['visible_tokens'] for x in g]):>9}"
              f"{med([x['e2e_tok_s'] for x in g]):>11}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--only", choices=["anthropic", "openai"])
    ap.add_argument("--out", default="results.jsonl")
    ap.add_argument("--fast", action="store_true", help="Claude speed=fast (Opus 5.5 only) / OpenAI service_tier=fast")
    ap.add_argument("--summarize", action="store_true", help="only print a summary of --out")
    a = ap.parse_args()
    global FAST
    FAST = a.fast

    if a.summarize:
        summarize([json.loads(l) for l in open(a.out)])
        return

    jobs = []
    if a.only != "openai":
        if anthropic_key():
            jobs += [("anthropic", m) for m in CLAUDE_MODELS if not FAST or m in CLAUDE_FAST_MODELS]
        else:
            print("No ANTHROPIC_API_KEY / BENCH_ANTHROPIC_API_KEY set; skipping Claude models.", file=sys.stderr)
    if a.only != "anthropic":
        jobs += [("openai", m) for m in OPENAI_MODELS]

    # One thread per model; runs within a model are sequential.
    with ThreadPoolExecutor(len(jobs)) as ex:
        results = list(ex.map(lambda j: bench_model(j[0], j[1], a.runs, a.out), jobs))
    summarize([r for rs in results for r in rs])


if __name__ == "__main__":
    main()
