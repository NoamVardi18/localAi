# LocalAi — KNOWLEDGE.md

One source of truth: what this project is, why it exists, where things live, current state.
Not a code repo — a wargame + one-shot install/verify run. Archived 2026-07-10 (moved from
`~/Claude/LocalAi`, a one-line pointer stub now lives there). Remote:
`github.com/NoamVardi18/localAi` (private-by-default use case, check before making public).

## WHAT
A fully local, offline-capable, fully open-source AI stack built and verified on Noam's Mac
(M5 Pro, 48GB, macOS 26.4) via Ollama — a dense daily-driver model, a fast MoE lane, a small
fallback, and a Hebrew-capable embedding model wired for vault RAG (Obsidian + Second Brain).

## WHY
Noam wanted private doc chat over his vaults (needs Hebrew-quality embeddings, not assumed),
coding help, English+Hebrew first drafts, and — stretch goal — offloading cheap/mechanical
agent tasks off paid API tokens, all with **nothing leaving the box** (post-Composio-breach
privacy posture) and no closed-source tools even if free (disqualifies e.g. LM Studio's GUI).

## WHERE (key files)
- `RECON-SEED.md` — settled machine facts (M5 Pro/48GB/803GB free, Ollama 0.30.11 pre-installed,
  qwen3:30b-a3b pre-pulled) + Jan-2026 model-landscape hypotheses to verify, not trust blind.
- `localai.md` — the wargame order + full mission brief (the executor's verbatim orders).
- `wargames/00-localai-stack.md` — the move-by-move wargame plan (recon → build → verify),
  right-sized (single wargame file, no red-team waves — "low-risk reversible single-machine install").
- `wargames/answers/RUN-REPORT.md` — **the actual run**, executed live by Sonnet: every move's
  result against its success bar, all 6 functional criteria + 2 data criteria (licenses,
  hardware verdict).
- `wargames/answers/rag-scratch.py`, `payload-hebrew-embed-test.py`, `payload-offline-battery.sh`
  — the verification scripts (RAG probe, Hebrew embedding bake-off, wifi-off privacy battery).
- `KICKOFF-PROMPT.md` — paste-ready prompt used to launch the wargame session.

## STATE (2026-07-10, WARGAME COMPLETE)
All 6 functional success criteria PASS (persistent 127.0.0.1-only service @ ctx 32768; tok/s
measured — dense **qwen3.6:27b 12.7 tok/s** under its 15 bar but no error, MoE **qwen3:30b-a3b
69-83 tok/s** well over bar, fallback **qwen3.5:4b 63.5 tok/s** over bar; coding/English PASS,
Hebrew 4/5+5/5 usable-with-flaws; embedding tie broken to **qwen3-embedding** over bge-m3;
vault RAG PASS on Hebrew/English/Second Brain notes; offline wifi-off battery PASS, nothing
phones home). Licenses all OSI. Hardware verdict: viable as a local drafting+RAG+agent-offload
stack; NOT a snappy interactive daily-driver at the dense 27B's 12.7 tok/s — prefer the MoE
lane for speed. **Stack was deliberately SHUT DOWN** after the run (Noam's order — no idle
20GB+ resident models); LaunchAgent `com.noam.ollama` disabled. Re-enable: `launchctl enable
gui/501/com.noam.ollama && launchctl bootstrap gui/501 ~/Library/LaunchAgents/com.noam.ollama.plist`.

## OPEN
- Obsidian `copilot` plugin files are installed (`~/Claude/Obsidian/.obsidian/plugins/copilot/`)
  but NOT committed (vault `.gitignore` excludes plugin dirs) — Noam still needs the 3-line
  in-app setup (enable plugin, point chat model + embedding model at the local Ollama endpoint).
- Stack is currently OFF — re-enable before actually using vault chat / agent-offload day to day.
- Known RAG weak spot: link-heavy "pointer" notes retrieve poorly under naive cosine top-2
  (not fixed, documented as a real limitation).
