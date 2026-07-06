# 00 — LOCAL AI STACK (single-mission wargame, WG5)

> Executor: **Sonnet**, Claude Code, running ON the target Mac. This is the entire wargame —
> one mission by right-sizing order (localai.md, Fable verdict 2026-07-06): no other mission
> files exist, no RUN-ALL, no style bible. The two `payload-*.{py,sh}` files in this folder are
> tested artifacts this mission invokes — use them verbatim, do not rewrite them.
> Write your run report into `answers/RUN-REPORT.md` section by section AT each move's
> completion, never batched at the end. Deviations recorded honestly.

## GOAL + WHY
A fully local, open-source AI stack on Noam's MacBook Pro (M5 Pro, 48 GB): one quality daily
driver, one fast MoE lane for agent offload, one small fallback, one Hebrew-tested embedding
model, 32k context configured, vault RAG working over his Obsidian notes, and a wifi-off
proof that nothing phones home. WHY: post-Composio-breach privacy (nothing leaves the box is
a HARD requirement), Hebrew drafting is load-bearing (his notes are Hebrew — a stack that only
works in English fails), and every haiku-tier task moved local stops burning paid API quota.
Failure cost: a half-configured stack that silently falls back to defaults (4k context, wrong
embedder) looks fine in a demo and fails on his real vault.

## SUCCESS CRITERIA (all must hold at VERIFY)
1. Runtime running as a persistent service, bound to 127.0.0.1 only, context ≥32768 confirmed via `ollama ps`.
2. Daily driver + fallback + MoE lane pulled, each with a MEASURED tok/s on this machine (recorded numbers, not vibes) meeting its bar (M5).
3. Coding, English-draft, Hebrew-draft use cases each exercised once with recorded output + grade (M6).
4. Embedding model chosen BY the Hebrew retrieval test result (≥5/6), not by reputation (M7).
5. Vault RAG answers one Hebrew and one English question from real Obsidian-vault notes PLUS one question from a Second Brain note, correctly, fully locally (M8).
6. Offline battery passes: generation + embedding work with wifi OFF; no non-localhost connections (M9).
7. Every installed component's license verified genuinely open source (table in RESULT filled with license names).
8. Plain hardware verdict written: what this box can and cannot run as a daily driver.

## RECON — SETTLED (do not re-derive)
Machine (verified on the box 2026-07-06): macOS 26.4 (25E246), M5 Pro 18-CPU/20-GPU, 48 GB
unified, ~803 GB free disk. Ollama **0.30.11 via Homebrew** (`/opt/homebrew/bin/ollama`;
`brew services` knows it, state `none` = not running; **no Ollama.app in /Applications** —
so no GUI auto-updater exists on this box). `qwen3:30b-a3b` already pulled (~17 GB store).
Wifi device = **en0**. Python **3.14.6** at `python3`. Obsidian.app installed; human vault
`~/Claude/Obsidian` (git-synced, notes repo = auto-push OK) with plugins dataview/git/
quickadd/templater — no RAG plugin yet. Mac is a daily driver under heavy load: model budget
≤ ~24 GB, leave 10+ GB headroom; the ~36 GB Metal wired ceiling is NOT the planning number.

Web recon (verified 2026-07-06, four independent researcher passes, sources in
`RECON-SOURCES.md` if present, else the session log):
- **Ollama**: latest stable **v0.31.1** (2026-06-30). Core server+CLI = MIT. Default bind
  still 127.0.0.1:11434. Since ~v0.19 (March 2026) Ollama ships an **MLX engine** for Apple
  Silicon 32 GB+ — already inside the installed 0.30.11, no separate mlx-lm needed. Flash
  Attention: official FAQ says auto-on when supported; KV-cache quantization
  (`OLLAMA_KV_CACHE_TYPE=q8_0`) only takes effect where flash attention is active, silently
  falls back to f16 otherwise. Context default is now VRAM-tiered (24–48 GiB → 32k), but the
  two official docs pages contradict each other — we set it explicitly and trust nothing.
  No official telemetry statement found (third-party sources only say "none") → the wifi-off
  battery is the proof, not the docs.
- **Models (landscape moved since Jan-2026)**: **Qwen3.6-27B dense** (2026-04-22, Apache 2.0,
  official tag `qwen3.6:27b`, **17 GB Q4_K_M**, 262k ctx) is the current best open daily
  driver in this memory class — verified on ollama.com/library + Ollama's own announcement.
  **Gemma 4** (2026-04-02, Apache 2.0 — first fully-OSS Gemma, tags `gemma4:e2b/e4b/26b/31b`)
  is the #2 / Hebrew fork target. **Qwen3.5** family (Feb 2026, Apache 2.0, `qwen3.5` library
  incl. 4b/9b) supersedes Qwen3-4B/8B for the small slot. Mistral "Small 4" is now 119B-A6B —
  too big, ignore. The already-pulled `qwen3:30b-a3b` (Apache 2.0) is one generation old but
  on-disk and its 3B-active MoE is the fastest thing here (~1.5–2× dense tok/s on Apple
  Silicon) — keep it as the agent-offload lane rather than re-downloading a MoE.
  **DictaLM-3.0-24B** (Hebrew-native, Bar-Ilan) exists but has NO confirmed Ollama/GGUF path —
  escalation only, not a move.
- **Embeddings**: `qwen3-embedding` (Apache 2.0; `:0.6b` = 639 MB/32k ctx default tag) tops
  multilingual MTEB; `bge-m3` (MIT, official tag, 1.2 GB/8k ctx/1024-dim) is the tested
  incumbent. **No vendor itemizes Hebrew support** — the smoke test decides, period. Note:
  Ollama's `/api/embed` exposes bge-m3's dense vector only (no sparse/ColBERT) — fine for
  this RAG, worth knowing.
- **Licenses — DISQUALIFIED**: LM Studio (proprietary GUI), **Open WebUI** (custom non-OSI
  license since Apr 2025, own FAQ admits it), **Smart Connections** Obsidian plugin (custom
  non-OSI license since Dec 2025). QUALIFIED: Jan (Apache 2.0, fallback chat UI),
  **obsidian-copilot** by logancyang (main RAG UX path — license check is R5 below).

## RECON NEEDED (executor settles each at the marked move; record answers in RUN-REPORT)
| # | question | exact check | used at |
|---|----------|-------------|---------|
| R1 | does brew already carry ≥0.31.1? | `brew info ollama \| head -3` | M2 |
| R2 | context actually 32768 after config? | `ollama ps` → CONTEXT column | M3 |
| R3 | flash attention + q8_0 KV active for our archs? | server log: `grep -iE "flash\|kv cache" ~/Library/Logs/ollama.log` after loading each model | M4 |
| R4 | `qwen3.5:4b` exact size on pull | `ollama pull` output | M4 |
| R5 | obsidian-copilot license is OSI? | `curl -s https://raw.githubusercontent.com/logancyang/obsidian-copilot/master/LICENSE \| head -5` (expect AGPL-3.0; also check ollama.com pages of each pulled model show Apache-2.0/MIT as recon claimed) | M8 |
| R6 | `gemma4:31b` fits ≤24 GB? | pull-size line — ONLY if Hebrew fork fires | M6-fork |

## MEMORY BUDGET (planning table — one big model loaded at a time)
| slot | model | weights (Q4) | +KV @32k (est) | verdict |
|------|-------|--------------|----------------|---------|
| daily | qwen3.6:27b | 17 GB | ~2–4 GB | ~21 GB peak — inside the ≤24 GB rule |
| MoE lane | qwen3:30b-a3b (on disk) | 17 GB | ~2–3 GB | ~20 GB peak — never load both big models at once |
| fallback | qwen3.5:4b | ~2.6 GB | <1 GB | trivial |
| embed | winner of M7 | 0.6–1.2 GB | — | can co-load with either big model |

70B-class @ q4 ≈ 40+ GB: loads only by stealing the headroom real work needs — **not a daily
driver on this box**. That sentence is the honest answer if anyone asks for bigger (criterion 8).

## PRE-FLIGHT (run all before M1; any FAIL → its counter, don't improvise)
- `df -h / | tail -1` → EXPECT ≥100 GB free. FAIL → disk anomaly since recon; STOP, flag Noam.
- `/opt/homebrew/bin/ollama --version` → EXPECT `0.30.11` (+ "could not connect" warning — normal, server is down). FAIL (command missing) → brew install drifted; `brew reinstall ollama`.
- `pgrep -x ollama` → EXPECT empty. FAIL (running) → someone started it; `ollama ps` to see loaded models, then continue from M3 (skip M2 upgrade this run, note deviation).
- `ls ~/.ollama/models/manifests/registry.ollama.ai/library/` → EXPECT `qwen3`. FAIL → pulled model gone; add `qwen3:30b-a3b` to M4's pull list (~17 GB extra download).
- `python3 payload-hebrew-embed-test.py --selftest` (run from this folder) → EXPECT `SELFTEST OK 6/6`. FAIL → payload corrupted; restore from git before proceeding.

## MOVES

**M1 — baseline snapshot.**
`brew list --versions ollama; ollama --version 2>&1; ls -la ~/.ollama/models/manifests/registry.ollama.ai/library/; df -h / | tail -1`
EXPECT: versions + model list print; record all in RUN-REPORT as the rollback reference.
FAIL: n/a (read-only). This move exists so every later change has a before-picture.

**M2 — upgrade Ollama via brew (R1).**
`brew upgrade ollama && ollama --version 2>&1`
EXPECT: version ≥0.31.1 (client line; server warning still normal).
FAIL (brew formula still <0.31.1) → homebrew lag, not an error: **stay on the brew version,
do NOT curl-install from ollama.com** (unmanaged binary = update rot). 0.30.11 already has the
MLX engine; note the deviation and continue.
FAIL (upgrade breaks, `ollama` gone) → `brew reinstall ollama`; still broken → ABORT-1.

**M3 — persistent server with explicit context (the anti-default move).**
Write `~/Library/LaunchAgents/com.noam.ollama.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.noam.ollama</string>
  <key>ProgramArguments</key><array>
    <string>/opt/homebrew/bin/ollama</string><string>serve</string>
  </array>
  <key>EnvironmentVariables</key><dict>
    <key>OLLAMA_CONTEXT_LENGTH</key><string>32768</string>
    <key>OLLAMA_FLASH_ATTENTION</key><string>1</string>
    <key>OLLAMA_KV_CACHE_TYPE</key><string>q8_0</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/Users/vardi/Library/Logs/ollama.log</string>
  <key>StandardErrorPath</key><string>/Users/vardi/Library/Logs/ollama.log</string>
</dict></plist>
```
Then: `brew services stop ollama 2>/dev/null; launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.noam.ollama.plist && sleep 3 && curl -s http://127.0.0.1:11434/api/version`
EXPECT: JSON version reply. Then `lsof -iTCP:11434 -sTCP:LISTEN -P -n` → EXPECT a single
listener on `127.0.0.1:11434` (or `[::1]`), NOTHING on `*` or the LAN IP.
FAIL (bootstrap error "already loaded") → `launchctl bootout gui/$(id -u)/com.noam.ollama` then re-bootstrap.
FAIL (older launchctl syntax rejected) → `launchctl load -w ~/Library/LaunchAgents/com.noam.ollama.plist`.
FAIL (listener on 0.0.0.0) → an OLLAMA_HOST env leak; find it (`launchctl print gui/$(id -u)/com.noam.ollama | grep -i host`, check `~/.zshenv`), remove, restart service. Non-localhost bind is a privacy criterion — do not proceed past M3 with it wrong.
Never start the server any other way for the rest of the mission (two servers = port fight).

**M4 — pull the fleet (R3, R4).**
`ollama pull qwen3.6:27b && ollama pull qwen3.5:4b && ollama pull qwen3-embedding && ollama pull bge-m3`
EXPECT: sizes ≈ 17 GB / ~2.6 GB / ~639 MB / ~1.2 GB. Record actuals.
FAIL (`qwen3.6:27b` tag not found) → recon drift on the exact tag: `curl -s https://ollama.com/library/qwen3.6/tags | grep -o '27b[^"<]*' | sort -u` and use the closest official 27b q4 tag; none exists at all → FORK-BIG-B: daily driver = `gemma4:31b` (R6 check first), note deviation.
FAIL (`qwen3.5:4b` not found) → same probe on `qwen3.5`; fallback tag `qwen3.5:9b` (bigger, still fine).
FAIL (embedding tags not found) → probe library pages; both embedders missing → ABORT-2 (registry unreachable ≠ offline goal; check network).
After each big-model pull, load it once (`ollama run <tag> "say ok" --verbose`) and run R3's
log grep. EXPECT: flash attention enabled lines for the dense models; if qwen3moe (`qwen3:30b-a3b`)
shows no flash-attention → KV stays f16 for it — harmless, RECORD it, don't chase it.

**M5 — measured tok/s per model (criterion 2).**
For each of `qwen3.6:27b`, `qwen3:30b-a3b`, `qwen3.5:4b`:
```
curl -s http://127.0.0.1:11434/api/generate -d '{"model":"<TAG>","prompt":"Write 3 sentences about the sea.","stream":false}' \
 | python3 -c 'import json,sys;d=json.load(sys.stdin);print("tok/s:",round(d["eval_count"]/d["eval_duration"]*1e9,1),"| load_ms:",d.get("load_duration",0)//1_000_000)'
```
Run twice, keep the second (first includes model load). EXPECT bars: dense 27B ≥ **15 tok/s**
(expect 25–40), MoE ≥ **35** (expect 60+), 4B ≥ **40**. Record all three numbers.
FAIL (a model below bar) → check `ollama ps` for `100% GPU`; if it shows partial CPU →
memory pressure from other apps; close the big consumers, retry once. Still below bar →
RECORD the real number and continue (bars are quality gates for the verdict, not stop-signs) —
but a dense 27B under 10 tok/s means GPU offload is broken: check log for Metal errors, ABORT-3 if present.
FAIL (`eval_count` missing/HTTP error) → server crashed under load; `launchctl kickstart -k gui/$(id -u)/com.noam.ollama`, retry once; second crash on same model → drop that model, note it, continue with the rest.

**M6 — use-case battery: coding, English, Hebrew (criterion 3).**
All against `qwen3.6:27b` via `/api/generate` (stream:false), temperature default.
1. CODING: ask for a Python function `merge_intervals(intervals)` + 3 asserts. Extract the code
   block, run `python3 - <<'EOF' … EOF`. EXPECT: exit 0, asserts pass. FAIL → one retry with the
   error pasted back; second fail → grade coding=FAIL, continue.
2. ENGLISH DRAFT: "Draft a 120-word professional email postponing a project kickoff by one
   week." EXPECT: coherent, correct length ±30%, no repetition loops.
   FAIL (off-length/incoherent/looping) → one retry with the flaw named in the prompt; second
   fail → grade english=FAIL, continue (a dense 27B failing this signals a broken quant/load —
   cross-check M5's tok/s and R3's log before trusting the grade).
3. HEBREW DRAFT (the load-bearing one): prompt in Hebrew:
   `כתוב מייל מקצועי קצר (עד 100 מילים) ללקוח בשם דני, שמסביר שהפרויקט יתעכב בשבוע בגלל תלות בספק חיצוני, בטון מרגיע.`
   GRADE all five, executor reads Hebrew: (a) output entirely Hebrew — no mid-sentence English
   leakage; (b) gender/number agreement correct throughout; (c) no gibberish/looping;
   (d) instruction followed (length, addressee, calming tone); (e) natural modern Hebrew, no
   niqqud spam. PASS = 5/5. Repeat with a second prompt (summarize a given English paragraph
   INTO Hebrew) — same rubric.
FORK-HEBREW (trigger: either Hebrew prompt scores ≤3/5): pull `gemma4:31b` (R6 size check
first — must be ≤24 GB or the fork dies here), rerun both Hebrew prompts on it. If gemma4
passes → daily driver for Hebrew = gemma4:31b, qwen3.6:27b stays for coding; record the split.
**DAILY_TAG rule for every later move (M8/M9/M10/VERIFY):** DAILY_TAG = qwen3.6:27b normally;
if this fork split the role, DAILY_TAG = the Hebrew-passing model (Hebrew is load-bearing),
and VERIFY check 2 runs its VERIFY-OK probe against BOTH models.
If BOTH fail Hebrew → criterion 3 fails honestly: write in the verdict that no current
Ollama-native open model drafts Hebrew acceptably on this box and flag DictaLM-3.0-24B
(needs manual HF→GGUF conversion, HIGH patience) as the escalation for Noam to approve.
Do NOT attempt the conversion in this mission.

**M7 — embedding bake-off (criterion 4).**
`python3 payload-hebrew-embed-test.py qwen3-embedding` then `python3 payload-hebrew-embed-test.py bge-m3`
EXPECT: each prints per-query PASS/FAIL + `RESULT <model>: n/6`. Winner = higher score;
tie → qwen3-embedding (newer, bigger ctx). PASS bar: winner ≥5/6.
FAIL (both <5/6) → try `ollama pull qwen3-embedding:4b` (2.5 GB) and rerun; still <5/6 →
criterion 4 fails honestly; record scores, pick the least-bad, flag in verdict.
FAIL (HTTP error) → server or tag issue, see M4/M3 counters.
Record the winner as EMBED_MODEL — M8/M9 use it.

**M8 — vault RAG, both layers (criterion 5, R5).**
LAYER 1 (API, blind-executable): pick two REAL notes: `~/Claude/Obsidian/Notes/מטרות ותוכניות אחרי הצבא.md`
(Hebrew; exists per recon) and any English note ≥10 lines (find with
`grep -rlE '^[A-Za-z].{40,}' ~/Claude/Obsidian/Notes | head -5`, pick one). Chunk each note by
paragraphs, embed chunks + one question per note with EMBED_MODEL, retrieve top-2 chunks by
cosine (adapt the payload's `cosine()`; write your scratch script into `answers/`), then ask
the daily driver: question + retrieved chunks → answer. Hebrew question for the Hebrew note:
`מתי הצבא מסתיים ומה מתוכנן אחרי?` EXPECT: answer states mid-December 2026 + the note's actual
plans, in Hebrew. English note: ask something its text answers. GRADE: answer grounded in the
retrieved chunks (no invention) = PASS per note.
SECOND BRAIN (the brief names both vaults): pick one substantive note from
`~/Claude/Second_Brain` (`find ~/Claude/Second_Brain -name '*.md' -size +1k | grep -v CLAUDE.md | head -5`,
pick one, read it, ask a question its text answers) and run the same embed→retrieve→generate
loop. EXPECT: grounded answer = PASS.
FAIL (no .md notes >1k found) → Second Brain has no RAG-worthy content yet; record "Second
Brain scope: no substantive notes at run time, criterion 5 rests on the Obsidian vault" —
an honest note, not a mission failure.
FAIL (retrieval misses the right chunk, any vault) → chunking too coarse; re-chunk at ~500 chars, retry once; still failing → record FAIL, criterion 5 fails for that language/vault.
LAYER 2 (Noam's UX — plugin install, gated):
R5 license check FIRST. AGPL-3.0/MIT/Apache → proceed; anything custom/non-OSI → SKIP layer 2,
recommend Jan (Apache 2.0) in the verdict instead, criterion 5 rests on layer 1 alone.
Install: `mkdir -p ~/Claude/Obsidian/.obsidian/plugins/copilot` then download the latest
release assets (`main.js`, `manifest.json`, `styles.css`) from
`https://github.com/logancyang/obsidian-copilot/releases/latest` (use the GitHub API to
resolve asset URLs: `curl -s https://api.github.com/repos/logancyang/obsidian-copilot/releases/latest | python3 -c 'import json,sys;[print(a["browser_download_url"]) for a in json.load(sys.stdin)["assets"]]'`)
into that folder. Add `"copilot"` to `~/Claude/Obsidian/.obsidian/community-plugins.json`
(create as `["copilot"]` if the file doesn't exist; it's a JSON array — append, valid JSON).
The vault is a git repo: commit these plugin files (`git -C ~/Claude/Obsidian add -A && git -C ~/Claude/Obsidian commit -m "localai: obsidian-copilot plugin (WG5 M8)" && git -C ~/Claude/Obsidian push`) — notes repo, auto-push allowed.
EXPECT: 3 files present, JSON valid (`python3 -c 'import json;json.load(open("…/community-plugins.json"))'`).
NOAM-GATE: plugin settings (point chat to `http://127.0.0.1:11434` model=daily driver, embeddings
to EMBED_MODEL) are set inside Obsidian's UI on first open — leave Noam a 3-line instruction in
RUN-REPORT; do NOT fight the plugin's data.json blind.
FAIL (community-plugins.json edit rejected by Obsidian later) → harmless; Noam enables via
Settings→Community plugins; note it.

**M9 — offline privacy battery (criterion 6) — detached, NEVER inline.**
You (the executor) lose your own network when wifi drops. Therefore:
`nohup bash payload-offline-battery.sh <DAILY_TAG> <EMBED_MODEL> > /dev/null 2>&1 &`
then WAIT (sleep 240) and read `answers/offline-battery.txt`.
EXPECT in the file: `OK offline confirmed` + `OK offline generation` + `OK offline embedding`
+ `OK no non-localhost ollama connections` + `OK wifi restored`. ALL FIVE = pass; the lsof
"OK" line alone proves nothing (it also passes when the server is down).
FAIL (`FAIL-SETUP network still reachable`) → another interface (tether/ethernet) is up; disable it, rerun.
FAIL (offline generation failed) → a model tried to reach the registry at load: check the tag was fully pulled (`ollama ls`), rerun; persists → REAL phone-home suspicion — capture `~/Library/Logs/ollama.log` tail into RUN-REPORT and ABORT-4 (privacy is the mission).
FAIL (wifi not back) → `networksetup -setairportpower en0 on` yourself the moment you regain the session.

**M10 — agent-offload probe (stretch; skip only if quota/time forces it, record the skip).**
OpenAI-compat check: `curl -s http://127.0.0.1:11434/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"qwen3:30b-a3b","messages":[{"role":"user","content":"Classify as POSITIVE/NEGATIVE/NEUTRAL, one word: \"the deploy failed twice but the fix was easy\""}]}'`
EXPECT: valid OpenAI-shaped JSON, one-word-ish classification, and (from M5) MoE ≥35 tok/s.
Verdict rubric for RUN-REPORT: MoE ≥35 tok/s + correct classification → "haiku-tier offload
VIABLE — wire `http://127.0.0.1:11434/v1` as an OpenAI-compatible endpoint for mechanical
tasks"; below bar → "offload NOT worth it yet, numbers: …".
Watch: qwen3 hybrid tags may emit `<think>` blocks that break one-word answers — if so, retry
once with `"think": false` in an `/api/chat` call; if thinking still leaks, record that the
offload lane needs the instruct-2507 variant (`ollama pull` probe: `qwen3:30b-a3b-instruct-2507-q4_K_M`) — pull and retest only if the probe finds an official tag.

## ABORT CONDITIONS (stop + flag Noam via inbox-post, do not improvise)
- ABORT-1: Ollama broken after M2 counters — no runtime, nothing else can run.
- ABORT-2: registry unreachable during setup pulls (setup needs network; only the FINISHED stack must be offline).
- ABORT-3: Metal/GPU errors in server log with dense-27B under 10 tok/s — hardware/driver issue beyond this mission.
- ABORT-4: phone-home evidence in the offline battery — privacy is the point; escalate with the log tail.
- Anything requiring `sudo`: this mission never needs it; a step demanding it means you drifted — stop.

## VERIFY LOOP (fresh-context verifier, max 4 rounds, then escalate)
Spawn a **fresh sonnet verifier** with NO access to your RUN-REPORT claims. It independently runs:
1. `curl -s 127.0.0.1:11434/api/version` OK AND `lsof -iTCP:11434 -sTCP:LISTEN -P -n` shows localhost-only AND `launchctl print gui/$(id -u)/com.noam.ollama | grep -c state` ≥1.
2. `ollama run <DAILY_TAG> "reply exactly: VERIFY-OK"` returns VERIFY-OK (both models if FORK-HEBREW split the role — see M6's DAILY_TAG rule); `ollama ps` CONTEXT column shows ≥32768 while loaded.
3. `python3 payload-hebrew-embed-test.py <EMBED_MODEL>` reproduces ≥5/6 (or matches the recorded least-bad score if M7 failed honestly).
4. `answers/offline-battery.txt` exists and contains all five OK lines (reads the file itself).
5. RUN-REPORT contains: three tok/s numbers, Hebrew grades with the actual generated text pasted, license table filled (every component + license name), and the hardware verdict paragraph.
PASS = 5/5 → tick WG5. Any check false → fix → re-verify (round++).

## RESULT (executor fills — template)
- versions: ollama before/after · models+sizes pulled:
- service persistent + bind (criterion 1): launchctl state= · lsof listener= (must be 127.0.0.1-only)
- tok/s: 27B dense= · 30B-A3B MoE= · 4B= (second-run numbers)
- context confirmed (ollama ps): · flash-attn per model (R3):
- coding grade (M6.1, asserts ran?): · english-draft grade (M6.2):
- Hebrew grades (M6.3, both prompts + which model won) → DAILY_TAG=:
- embedding bake-off: qwen3-embedding= /6 · bge-m3= /6 → EMBED_MODEL=
- vault RAG: Hebrew note PASS/FAIL · English note PASS/FAIL · Second Brain note PASS/FAIL · plugin layer status:
- offline battery: (paste the OK/FAIL lines)
- licenses: ollama=MIT · qwen3.6=Apache-2.0 · qwen3.5=Apache-2.0 · qwen3:30b-a3b=Apache-2.0 · embedder= · obsidian-copilot= (from R5)
- agent-offload verdict (M10):
- HARDWARE VERDICT (criterion 8, plain sentences):

## VERIFIER LOG (right-sized: one fresh-verifier pass at authoring time; red-team/sim waves skipped per order)
- 2026-07-06 fresh-context verifier (blind, ran both payloads itself): initial FAIL with 4 defects —
  (1) M6 English sub-test lacked a FAIL/counter; (2) DAILY_TAG undefined after a FORK-HEBREW split,
  M9/VERIFY would guess; (3) RESULT template missed criteria 1+3 lines; (4) Second Brain silently
  dropped from RAG scope vs the brief. All four patched in place (M6 counter added, DAILY_TAG rule
  added, RESULT lines added, Second Brain check added to M8/criterion 5) → re-confirmed by the same
  verifier context. Payload evidence: hebrew-embed selftest 6/6; offline-battery bash -n clean +
  DRYRUN exercised all log paths.
