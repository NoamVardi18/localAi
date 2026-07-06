# RECON-SEED — pre-settled facts for the localai wargame (gathered 2026-07-06, Fable session)

> Two trust tiers. **MACHINE FACTS = settled, don't re-derive.** **LANDSCAPE NOTES = Jan-2026
> model knowledge — WEB-VERIFY current releases/versions before recommending; treat every name
> below as a starting hypothesis, not an answer.**

## MACHINE FACTS (settled, verified on the box 2026-07-06)
- macOS 26.4 (build 25E246), MacBook Pro 16", Apple **M5 Pro**, 18-core CPU (6E+12P), 20-core GPU.
- **48 GB unified memory.** Default Metal wired ceiling ≈ 75% → ~36 GB practically usable for model weights+KV before the OS fights back (raisable via `iogpu.wired_limit_mb`, but that's HIGH-patience territory — flag as a fork, not the main path).
- **~803 GB free disk** — model storage is a non-issue.
- **Ollama 0.30.11 already installed** (`/opt/homebrew/bin/ollama`); server NOT currently running.
- **`qwen3:30b-a3b` already pulled** (~/.ollama manifests confirm) — Noam already started down this road; the wargame should build on it or explicitly justify replacing it.
- No LM Studio / Jan / llamafile in /Applications.
- This Mac is a daily driver running heavy sessions (Chrome + multiple Claude Code sessions) — the model budget must leave ~10+ GB headroom for real life; do NOT plan the daily driver at the 36 GB ceiling.

## USE-CASE FACTS (from Noam's OS — settled)
- **Vault chat / RAG**: Obsidian human vault (`~/Claude/Obsidian`) + Second Brain machine vault (`~/Claude/Second_Brain`, graphify-indexed — graph.json infrastructure already exists). Embeddings must handle **Hebrew + English**.
- **Hebrew is load-bearing**: his notes and drafts are often Hebrew. Local models' Hebrew varies wildly — the verify battery MUST include a Hebrew generation + Hebrew retrieval test. A model that aces English and mangles Hebrew fails the mission.
- **Privacy is the point**: post-Composio-breach sensitivity; "nothing leaves the box" is a hard requirement, verified wifi-off, not a preference.
- **Stretch goal**: offload haiku-tier mechanical agent work (classification, formatting, summaries) from paid API models to local. Worth designing the daily driver's speed target around (needs real tok/s, not benchmark vibes).
- Patience: **MEDIUM** — one runtime, working defaults, no build-from-source unless a fork forces it.

## LANDSCAPE NOTES (Jan-2026 cutoff — VERIFY BEFORE USE)
- **Daily-driver class on this box (~q4, ≤24 GB)**: Qwen3-30B-A3B (MoE, ~3B active — very fast on Apple Silicon, already pulled; check thinking-mode toggle behavior in current Ollama), Qwen3-32B dense (stronger/slower), Gemma 3 27B, Mistral Small 3.x 24B. DeepSeek-R1 distills for reasoning-heavy work.
- **70B-class q4 ≈ 40+ GB** — loads, but violates the headroom rule above; not a daily driver on 48 GB shared with real work. Say so plainly if asked.
- **Embeddings**: bge-m3 (multilingual incl. Hebrew) is the hypothesis to beat; nomic-embed-text is the common default but weaker on Hebrew — TEST both on a real Hebrew note before choosing.
- **Runtimes**: Ollama (installed, lowest friction, true OSS) vs llama.cpp direct (max control) vs MLX-LM (often fastest on Apple Silicon, check current model coverage). **LM Studio is free but its GUI is NOT open source** — the brief's OSS constraint disqualifies it; don't recommend it as the main path.
- **Ollama specifics to check**: default context length is small (historically 4k) — vault chat needs 16-32k set explicitly (`num_ctx` / Modelfile); default bind is 127.0.0.1 (good — keep it); confirm current version's Qwen3 MoE support quality.
- **Open WebUI** (OSS) is the usual chat-UI layer over Ollama if a UI is wanted; a CLI/raw-API path may serve Noam's agent-offload goal better. Fork on actual need, don't default to installing a UI.

## FILES IN THIS FOLDER
- `localai.md` — THE WARGAME ORDER (placeholders already filled with this machine's facts + right-sizing verdict). Start there.
- `RECON-SEED.md` — this file.
- `KICKOFF-PROMPT.md` — the paste-ready prompt for the fresh Fable session.
- `wargames/` — the session writes its output here (`00-localai-stack.md`).
