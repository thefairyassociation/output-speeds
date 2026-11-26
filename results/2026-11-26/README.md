# 2026-11-26 run

Models: Claude Opus 5.5 / Sonnet 5.5 / Haiku 5.5, OpenAI gpt-6.2-astra / gpt-6.2-sol / gpt-6.1-terra / gpt-6-luna.
Efforts low → xhigh, 3 runs each, medians shown. Fast = Claude `speed="fast"` (Opus 5.5 only) / OpenAI `service_tier="fast"`.
All 192 runs succeeded. Single prompt, single time of day — treat small gaps as noise.

Files: `results_openai.jsonl`, `results_openai_fast.jsonl`, `results_claude.jsonl`, `results_claude_fast.jsonl`.

## Cross-provider ranking (high effort, chars/s)

Tokens/s isn't comparable across providers: on this prompt a Claude token averaged ~3.2 chars, an OpenAI token ~5.3.

| # | Model | chars/s |
|---|---|---|
| 1 | gpt-6-luna (fast tier) | 1030 |
| 2 | Opus 5.5 (fast mode) | 859 |
| 3 | Haiku 5.5 | 683 |
| 4 | gpt-6-luna | 646 |
| 5 | gpt-6.2-sol (fast tier) | 639 |
| 6 | gpt-6.1-terra (fast tier) | 601 |
| 7 | Sonnet 5.5 | 410 |
| 8 | gpt-6.1-terra | 347 |
| 9 | Opus 5.5 | 324 |
| 10 | gpt-6.2-sol | 321 |
| 11 | gpt-6.2-astra (fast tier) | 312 |
| 12 | gpt-6.2-astra | 178 |

## Claude

| Model | Effort | tok/s | chars/s | TTFT (s) | Total (s) | Thinking tok |
|---|---|---|---|---|---|---|
| Haiku 5.5 | low | 201 | 622 | 0.4 | 7.3 | 2 |
| | medium | 215 | 673 | 3.7 | 10.7 | 774 |
| | high | 224 | 683 | 7.0 | 13.9 | 1359 |
| | xhigh | 352 | 1096 | 20.9 | 24.9 | 4761 |
| Sonnet 5.5 | low | 131 | 412 | 0.6 | 14.2 | 2 |
| | medium | 128 | 399 | 0.5 | 14.2 | 2 |
| | high | 131 | 410 | 4.7 | 17.5 | 587 |
| | xhigh | 127 | 401 | 6.3 | 19.3 | 772 |
| Opus 5.5 | low | 101 | 325 | 0.9 | 18.1 | 55 |
| | medium | 103 | 328 | 5.5 | 21.8 | 575 |
| | high | 104 | 324 | 7.5 | 24.1 | 759 |
| | xhigh | 140 | 440 | 27.8 | 39.1 | 2951 |
| **Opus 5.5 fast** | low | 270 | 870 | 0.5 | 6.4 | 55 |
| | medium | 269 | 866 | 2.5 | 8.9 | 620 |
| | high | 272 | 859 | 3.0 | 8.9 | 785 |
| | xhigh | 270 | 868 | 3.7 | 9.9 | 958 |

## OpenAI — standard tier

| Model | Effort | tok/s | chars/s | TTFT (s) | Total (s) | Reasoning tok |
|---|---|---|---|---|---|---|
| gpt-6-luna | low | 143 | 786 | 1.4 | 8.6 | 88 |
| | medium | 133 | 702 | 4.1 | 10.7 | 416 |
| | high | 123 | 646 | 5.4 | 13.0 | 516 |
| | xhigh | 151 | 808 | 7.9 | 13.2 | 1034 |
| gpt-6.1-terra | low | 59 | 316 | 2.0 | 17.7 | 40 |
| | medium | 66 | 352 | 4.6 | 18.7 | 176 |
| | high | 64 | 347 | 9.6 | 24.4 | 516 |
| | xhigh | 65 | 351 | 35.0 | 48.2 | 2070 |
| gpt-6.2-sol | low | 52 | 279 | 0.8 | 18.2 | 0 |
| | medium | 55 | 295 | 0.9 | 16.7 | 0 |
| | high | 60 | 321 | 4.2 | 18.1 | 209 |
| | xhigh | 63 | 331 | 16.4 | 30.1 | 856 |
| gpt-6.2-astra | low | 34 | 181 | 1.2 | 26.8 | 0 |
| | medium | 37 | 195 | 1.3 | 24.2 | 0 |
| | high | 34 | 178 | 7.2 | 31.2 | 154 |
| | xhigh | 34 | 183 | 21.6 | 45.9 | 575 |

## OpenAI — fast tier

| Model | Effort | tok/s | chars/s | TTFT (s) | Total (s) | Speedup vs standard |
|---|---|---|---|---|---|---|
| gpt-6-luna | low | 204 | 1105 | 1.1 | 6.1 | 1.4× |
| | medium | 202 | 1088 | 2.5 | 7.1 | 1.5× |
| | high | 194 | 1030 | 4.9 | 9.4 | 1.6× |
| | xhigh | 205 | 1094 | 4.7 | 9.1 | 1.4× |
| gpt-6.2-sol | low | 120 | 645 | 0.9 | 8.2 | 2.3× |
| | medium | 121 | 649 | 0.6 | 8.1 | 2.2× |
| | high | 123 | 639 | 3.1 | 10.0 | 2.0× |
| | xhigh | 119 | 621 | 8.9 | 15.9 | 1.9× |
| gpt-6.1-terra | low | 108 | 580 | 1.6 | 10.3 | 1.8× |
| | medium | 106 | 573 | 3.4 | 11.9 | 1.6× |
| | high | 112 | 601 | 6.1 | 14.0 | 1.7× |
| | xhigh | 113 | 606 | 22.7 | 30.9 | 1.7× |
| gpt-6.2-astra | low | 58 | 312 | 1.1 | 15.4 | 1.7× |
| | medium | 60 | 323 | 0.8 | 14.9 | 1.6× |
| | high | 58 | 312 | 6.5 | 20.5 | 1.7× |
| | xhigh | 64 | 334 | 17.0 | 28.0 | 1.9× |

## Takeaways

- **Effort mostly changes TTFT, not decode speed.** Higher effort = more thinking before the first word; once text starts, each model streams at roughly the same rate at every level.
- **Opus 5.5 fast mode ≈ 2.7× standard Opus**, a bigger jump than any OpenAI fast tier (1.4–2.3×). It also cut xhigh TTFT from 28 s to 4 s, partly because it thought much less (~960 vs ~3000 tokens).
- **Opus 5.5 fast beats Haiku 5.5** on speed; only gpt-6-luna on the fast tier was faster.
- **Sonnet 5.5 and gpt-6.2-sol/astra barely think at low/medium** on this prompt, so they start almost instantly.
- **Opus and Haiku stream faster after long thinking at xhigh** (Haiku ~350 tok/s vs ~210, Opus ~140 vs ~100). Same-effort runs with less thinking were slower. Cause unknown from outside the API.
- **Claude wrote longer answers** to the same "~700 words" prompt (~5000 chars vs ~4400), which inflates its total time.
