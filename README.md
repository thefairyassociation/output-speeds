# output-speeds

Benchmarks streaming output speed of Claude and OpenAI models across effort levels (and fast mode).

## Results

| Date | Models | Notes |
|---|---|---|
| [2026-11-26](results/2026-11-26/README.md) | Opus/Sonnet/Haiku 5.5; gpt-6.2-astra, gpt-6.2-sol, gpt-6.1-terra, gpt-6-luna | standard + fast for all fast-capable models |

## What gets measured

Each run streams one response to a fixed prompt (~700-word explanation of TCP congestion control, see `PROMPT` in `bench.py`) and records:

| Metric | Meaning |
|---|---|
| `out_tok_s` | Visible-output decode speed: visible tokens ÷ (last text delta − first text delta). Unaffected by thinking. |
| `out_char_s` | Same in characters/s. **Use this to compare across providers** — tokenizers differ (~3.2 chars/token Claude vs ~5.3 OpenAI on this prompt). |
| `ttft_s` | Time to first *visible* text, so it includes all thinking/reasoning. |
| `total_s` | Wall time for the whole response. |
| `reasoning_tokens` | OpenAI reports this directly. For Claude it's `output_tokens` minus the visible-text token count (counted with `count_tokens`), since thinking display is omitted. |
| `e2e_tok_s` | All generated tokens (thinking + visible) ÷ total time. |
| `tier` | Speed tier the API says it actually served (`fast`/`default`/`standard`) — check this when using `--fast`. |

`max` effort is skipped on purpose (slow and expensive, not very informative). Default is 3 runs per model × effort; each model runs in its own thread, runs within a model are sequential. Use `--summarize` for median tables.

## Running it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

```bash
D=results/$(date +%F); mkdir -p $D
.venv/bin/python bench.py --only openai --out $D/results_openai.jsonl
.venv/bin/python bench.py --only openai --fast --out $D/results_openai_fast.jsonl
.venv/bin/python bench.py --only anthropic --out $D/results_claude.jsonl
.venv/bin/python bench.py --only anthropic --fast --out $D/results_claude_fast.jsonl
```

Re-print a summary from saved results:

```bash
.venv/bin/python bench.py --summarize --out results/2026-11-26/results_claude.jsonl
```

### Testing new models

Either update `CLAUDE_MODELS` / `OPENAI_MODELS` (and `CLAUDE_FAST_MODELS`) at the top of `bench.py`, or pass them ad hoc:

```bash
.venv/bin/python bench.py --models claude-new-model,gpt-new-model --efforts low,medium,high,xhigh --out $D/results_new.jsonl
```

Provider is inferred from the ID (`claude-*` → Anthropic, anything else → OpenAI). With `--models`, `--fast` is sent to every model listed, so only list fast-capable ones.

Checklist when a new generation drops:
1. Find exact OpenAI IDs: `curl -s https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" | python3 -m json.tool | grep '"id"'`. Claude IDs are in Anthropic's models docs (or `GET https://api.anthropic.com/v1/models`).
2. Check accepted effort levels — a bad value returns a 400 that lists the supported ones.
3. Check which Claude models support `speed="fast"` (only Opus 5.5 as of 2026-11).
4. Run all four passes, write `results/<date>/README.md` (copy the previous one as a template), add a row to the table above.

## API notes

- **Claude:** `thinking={"type": "adaptive"}`, `output_config={"effort": ...}`, fast mode is top-level `speed="fast"`. The script pins `base_url="https://api.anthropic.com"` because `ANTHROPIC_BASE_URL` may point elsewhere in some environments.
- **OpenAI:** Responses API, `reasoning={"effort": ...}`, fast tier is `service_tier="fast"`.

## Claude Code cloud environment setup

If you run this in a Claude Code cloud session:
- **Network:** `api.openai.com` must be on the environment's allowed hosts (already added to the "output speeds" environment). `api.anthropic.com` is reachable by default.
- **Anthropic key:** Claude Code hides `ANTHROPIC_API_KEY` from the shell, so put the key in an environment variable named **`BENCH_ANTHROPIC_API_KEY`** (the script reads either). Network secrets can't be used for Anthropic's API.
- **OpenAI key:** `OPENAI_API_KEY` as an environment variable works as-is.
