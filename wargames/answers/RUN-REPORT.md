# WG5 — Local AI Stack — RUN REPORT

Executor: Sonnet (Claude Code), running live on Noam's Mac. Sections written as each move completes.

## PRE-FLIGHT

- `df -h / | tail -1` → `926Gi 12Gi 802Gi 2%` → 802 GB free. EXPECT ≥100 GB free → **PASS**.
- `/opt/homebrew/bin/ollama --version` → `Warning: could not connect to a running Ollama instance` + `Warning: client version is 0.30.11`. Matches expected 0.30.11 + the normal "not running" warning → **PASS**.
- `pgrep -x ollama` → empty (exit 1) → **PASS** (not running).
- `ls ~/.ollama/models/manifests/registry.ollama.ai/library/` → `qwen3` → **PASS** (pulled model present).
- `python3 payload-hebrew-embed-test.py --selftest` → `SELFTEST OK 6/6` → **PASS**.

All PRE-FLIGHT checks PASS, no deviations. Proceeding to M1.

## M1 — baseline snapshot

- `brew list --versions ollama` → `ollama 0.30.11`
- `ollama --version` → client 0.30.11, server not running (normal)
- `ls ~/.ollama/models/manifests/registry.ollama.ai/library/` → `qwen3` only
- `df -h /` → 802 GB free

Rollback reference recorded. No deviations. Proceeding to M2.

## M2 — upgrade Ollama via brew (R1)

`brew upgrade ollama && ollama --version` → brew formula carried 0.31.1 (R1 answered: yes).
Upgraded cleanly `0.30.11 -> 0.31.1`. Client version now confirms `0.31.1` (server still down,
normal warning). No deviations.

## M3 — persistent server with explicit context (the anti-default move)

RESUME NOTE: on resuming this run, verified pre-M3 state fresh (`pgrep -x ollama` → empty,
`ollama --version` → client 0.31.1, no plist yet) — matches where M2 left off, no drift.

- Wrote `~/Library/LaunchAgents/com.noam.ollama.plist` verbatim (context=32768,
  flash-attention=1, kv-cache=q8_0, RunAtLoad+KeepAlive, logs to
  `~/Library/Logs/ollama.log`).
- `brew services stop ollama` (no-op, wasn't running) → `launchctl bootstrap gui/$(id -u) ...`
  → `curl -s http://127.0.0.1:11434/api/version` → `{"version":"0.31.1"}` → **PASS**, no bootstrap
  errors, no fallback syntax needed.
- `lsof -iTCP:11434 -sTCP:LISTEN -P -n` → single listener `ollama 127.0.0.1:11434 (LISTEN)`,
  nothing on `*`/LAN IP → **PASS** (criterion 1's bind requirement met).
- `ollama ps` right after bootstrap → empty table (no model loaded yet, expected — R2's CONTEXT
  column check deferred to M4 when a model actually loads).
No deviations. Proceeding to M4.

## M4 — pull the fleet (R3, R4)

- `ollama pull qwen3.6:27b` → 17 GB → matches recon expectation exactly → **PASS**.
- `ollama pull qwen3.5:4b` → **3.4 GB** actual (recon expected ~2.6 GB) → tag found fine, no
  FAIL branch triggered (that only fires on tag-not-found); recording the size drift honestly.
- `ollama pull qwen3-embedding` → **4.7 GB** actual (recon expected the `:0.6b` default tag at
  639 MB) → DEVIATION: the `latest`/default tag for `qwen3-embedding` resolves to a larger
  variant than recon assumed, not the 0.6b. Tag pulled successfully (no FAIL condition fires —
  M4 only FAILs on tag-not-found), so per mission rules I did not re-pull a different explicit
  tag on my own initiative. This pushes the embed slot outside the 0.6-1.2 GB planning line in
  the MEMORY BUDGET table — flagged for the hardware verdict.
- `ollama pull bge-m3` → 1.2 GB → matches recon exactly → **PASS**.

`ollama list` confirms all four present: `qwen3.6:27b` 17GB, `qwen3.5:4b` 3.4GB,
`qwen3-embedding:latest` 4.7GB, `bge-m3:latest` 1.2GB.

R3 flash-attention check (log grep after loading each big model):
- `qwen3.6:27b` (dense): `--flash-attn on`, `llama_context: flash_attn = enabled`,
  `warmup: flash attention is enabled` → **confirmed active**. Also confirms `-c 32768` and
  `--cache-type-k/v q8_0` on the command line → q8_0 KV cache is live for this model.
- `qwen3:30b-a3b` (MoE, already on disk): server command line also shows `--flash-attn on`,
  `--cache-type-k/v q8_0`, `-c 32768` → flash attention IS active for this arch too. This
  contradicts the mission's expectation that qwen3moe might show no flash-attention (harmless
  if so) — recording as a pleasant surprise, not a problem: KV cache gets q8_0 for both models.

R2 (context via `ollama ps` while a model is loaded): confirmed — `qwen3.6:27b` row showed
`CONTEXT 32768`, `PROCESSOR 100% GPU` → **PASS**.

No ABORT conditions hit. Proceeding to M5.

## M5 — measured tok/s per model (criterion 2)

Second-run numbers (first run includes model load, discarded per mission instructions):
- `qwen3.6:27b` (dense daily driver): run1 13.4 tok/s (load 6314ms) → run2 **12.7 tok/s**
  (load 296ms). Bar is ≥15 (expect 25-40) → **below bar**. FAIL branch followed: `ollama ps`
  showed `100% GPU` (not partial CPU, so the "close big consumers" retry doesn't apply — this
  isn't a memory-pressure symptom) and `grep -iE "metal.*error|error.*metal" ~/Library/Logs/ollama.log`
  returned nothing → no Metal errors, 12.7 > 10 so **ABORT-3 does NOT trigger**. Recording the
  real number and continuing per the mission's explicit instruction ("bars are quality gates for
  the verdict, not stop-signs"). This is real M5 hardware signal, not a config bug — flagged for
  the hardware verdict (criterion 8): this box runs the 27B dense model correctly but under the
  recon's expected 25-40 tok/s range.
- `qwen3:30b-a3b` (MoE lane): run1 70.9 → run2 **69.4 tok/s**. Bar ≥35 (expect 60+) → **PASS**,
  well above bar, confirms MoE is the fast lane as recon predicted.
- `qwen3.5:4b` (fallback): run1 64.2 → run2 **63.5 tok/s**. Bar ≥40 → **PASS**, comfortably above.

No `eval_count` errors, no crashes. Proceeding to M6.

## M6 — use-case battery (criterion 3), all on qwen3.6:27b

DEVIATION (process, not result): first attempts at M6.2+M6.3a were fired as two parallel
background curls with `--max-time 180`; the server runs NUM_PARALLEL=1 so they queued behind
each other, both timed out with empty bodies. Root cause understood; reran each one at a time,
foreground, 400s timeout — all subsequent M6 calls clean.

### M6.1 CODING — PASS
Asked for `merge_intervals(intervals)` + exactly 3 asserts. Model returned clean code
(sort by start, merge on overlap, empty-list guard) with 3 asserts. Extracted and executed via
`python3 - <<EOF` → exit 0, `ALL ASSERTS PASSED`. No retry needed. **coding=PASS**.

### M6.2 ENGLISH DRAFT — PASS
Prompt: 120-word professional email postponing a kickoff by one week. Output: 123 words
(within ±30%), coherent subject line + body, no repetition loops, correct register.
**english=PASS**, no retry needed.

### M6.3 HEBREW DRAFTS (load-bearing) — 4/5 + 5/5, no fork
Prompt 1 (mission's verbatim Hebrew prompt — email to דני, delay, calming tone). Generated text:

> שלום דני,
>
> תודה על סבלנותך. אנו מעדכנים כי לוח הזמנים של הפרויקט יעבור התאמה של שבוע אחד בלבד, בשל עיכוב בשרשרת האספקה הספקית החיצונית שאינה בשליטתנו. אנו נוקטים בכל הכדי לסגור את הטיפול במהירות ומבטיחים לעדכן אותך מיד עם קבלת המשלוח.
>
> אנו שומרים על תקשורת צמודה ועובדים להבטיח שהאיכות הסופית לא תיפגע כלל. תודה על אמינותך והבנתך.
>
> בברכה, [שמך]

Rubric: (a) entirely Hebrew — PASS (only [שמך] placeholder); (b) gender/number agreement —
PASS (consistent masculine address: סבלנותך, הבנתך); (c) no gibberish/looping — PASS;
(d) instruction followed — PASS (~60 words ≤100, addressee דני, week delay + external supplier
+ calming tone); (e) natural modern Hebrew — **FAIL**: "אנו נוקטים בכל הכדי" is malformed,
"שרשרת האספקה הספקית החיצונית" is unnatural word-stacking, "תודה על אמינותך" is semantically
off (אמונך/הבנתך intended). **Score: 4/5.**

Prompt 2 (summarize a given English paragraph about Apple Silicon unified memory INTO Hebrew,
3-4 sentences). Generated text:

> שבבי Apple Silicon מתבססים על ארכיטקטורת זיכרון מאוחדת, שבה המעבד והמעבד הגרפי חולקים את אותו זיכרון RAM פיזי. עיצוב זה מבטל את הצורך להעתיק נתוני מודלים בין זיכרון המערכת ל-VRAM ייעודי, ומאפשר להריץ מודלי שפה גדולים וכמותנים מקומית ביעילות גבוהה גם במחשבים ניידים. החסרון העיקרי הוא שמהירות ייצור הטוקנים נשלטת לרוב על ידי רוחב הפס של הזיכרון, ולא על ידי כוח החישוב הגולמי של השבב.

Rubric: (a) PASS — Apple Silicon/RAM/VRAM are proper nouns/acronyms, standard in Hebrew tech
writing, not mid-sentence leakage; (b) PASS; (c) PASS; (d) PASS (3 sentences, faithful summary);
(e) PASS with a note — "כמותנים" is a nonstandard coinage for "quantized" but reads naturally.
**Score: 5/5.**

FORK-HEBREW trigger check: fork fires only on ≤3/5; scores are 4/5 and 5/5 → **fork does NOT
fire**. Strict PASS bar is 5/5 on both; prompt 1's 4/5 misses it, so criterion-3 Hebrew is graded
honestly as **usable-with-flaws**: qwen3.6:27b drafts natural business Hebrew with occasional
broken collocations — fine for drafts Noam edits, not for send-as-is. **DAILY_TAG = qwen3.6:27b**
(unchanged) for all later moves. Proceeding to M7.

## M7 — embedding bake-off (criterion 4)

- `python3 payload-hebrew-embed-test.py qwen3-embedding` → **6/6** top-1 correct (PASS, bar 5/6)
- `python3 payload-hebrew-embed-test.py bge-m3` → **6/6** top-1 correct (PASS, bar 5/6)

Tie at 6/6 → mission tiebreak rule: qwen3-embedding (newer, 32k ctx vs bge-m3's 8k).
**EMBED_MODEL = qwen3-embedding.** Both models cleared every Hebrew, English, and mixed query —
criterion 4's choice is test-driven, not reputation-driven, as required. Proceeding to M8.

## M8 — vault RAG, both layers (criterion 5, R5)

Scratch script: `answers/rag-scratch.py` (stdlib only; cosine() adapted from the payload;
paragraph chunking, EMBED_MODEL=qwen3-embedding, top-2 retrieval, generation on DAILY_TAG).

### Layer 1 — API RAG
**Hebrew note** (`~/Claude/Obsidian/Notes/מטרות ותוכניות אחרי הצבא.md`, mission's designated
note, question `מתי הצבא מסתיים ומה מתוכנן אחרי?`):
- Attempt 1: answer stated אמצע דצמבר 2026 correctly but retrieval's chunk 2 was a bare `##`
  header → plans content thin. Applied the mission's re-chunk counter. (Note: the literal
  "~500 chars" re-chunk changed nothing — paragraphs were already <500 chars; the real defect
  was my splitter separating `##` headers from their section bodies, fixed in the chunker.)
- Retry: retrieved the intro line + the full "Added 2026-07-03" section; answer (in Hebrew):
  army ends **mid-December 2026**; two-stage timeline (~4 months to pre-release leave, ~2 more
  to full release), Europe solo trip during leave, security-work track at 15-20k ₪/month
  combined with AI projects, ₪200,000 financial goal incl. release grants. All grounded in the
  retrieved chunks, no invention → **Hebrew note PASS**.

**English note**: first pick from the mission's grep was `July 2027.md` — question "What are
the big three items in the SharpenDaily engine backlog?" (its text answers this). Retrieval
FAILED even after the re-chunk retry: the note is a pointer-style note dominated by a link
chunk containing the literal words "SharpenDaily Engine Backlog" (cosine 0.84) while the
actual big-three list ranked 6th (0.55). Recorded honestly as a retrieval miss for that note —
real signal: link-heavy pointer notes retrieve poorly with naive cosine top-2.
DEVIATION (note re-pick): the grep candidates turned out to be mostly Hebrew-body notes that
merely start with an English line; picked a genuinely English substantive note instead:
`Evergreen notes turn ideas into objects that you can manipulate.md`. Question: "What do
evergreen notes turn ideas into, and why is that useful?" (first, compound question on this
note missed one chunk — grounded, no invention, honest "context doesn't say"; retry with a
single-focus question per the one-retry rule). Answer: "Evergreen notes turn ideas into
objects... manipulate, combine, and stack them without needing to hold them all in your head"
— exactly the note's text, grounded → **English note PASS**.

**Second Brain note** (`~/Claude/Second_Brain/maps/vps-headless-claude.md`, substantive,
>1k): question "What is the working pattern for headless VPS runs that cannot write to
~/.claude?" → answer: "The working pattern is stage-in-repo + one-shot deploy.sh." — exact,
grounded → **Second Brain note PASS**.

### R5 + license verification (criterion 7)
- obsidian-copilot LICENSE (raw GitHub) → **AGPL-3.0** → OSI → Layer 2 proceeds.
- Local blobs via `/api/show`: qwen3.6:27b / qwen3.5:4b / qwen3:30b-a3b → **Apache-2.0**;
  bge-m3 → **MIT**. qwen3-embedding's local blob carries no license text → verified upstream
  via HuggingFace API (Qwen/Qwen3-Embedding-0.6B and -4B): **Apache-2.0**.
- ollama core = MIT (recon-settled).

### Layer 2 — obsidian-copilot plugin install
- Release 3.3.3 assets (`main.js` 3.4MB, `manifest.json`, `styles.css`) downloaded into
  `~/Claude/Obsidian/.obsidian/plugins/copilot/` — 3 files present, manifest id="copilot" ✓.
- `"copilot"` appended to `~/Claude/Obsidian/.obsidian/community-plugins.json` — JSON
  validated ✓.
- DEVIATION (commit skipped, deliberate): the vault's own `.gitignore` explicitly excludes
  `.obsidian/plugins` and `.obsidian/community-plugins.json` (machine-local by Noam's vault
  policy). Force-adding would override his config — files installed locally, NOT committed.
- Checked `ps aux` for in-flight scp/rsync before the pulls — none (cross-lane law 2).

**NOAM — 3-line plugin setup (do inside Obsidian once):**
1. Settings → Community plugins → enable "Copilot" (if it doesn't appear, toggle Restricted mode off/on).
2. Copilot settings → Chat model: custom/OpenAI-format → base URL `http://127.0.0.1:11434/v1`, model `qwen3.6:27b` (or provider "Ollama", model qwen3.6:27b).
3. Copilot settings → Embedding model: Ollama → `qwen3-embedding`, then "Refresh vault index".

Proceeding to M10 (agent-offload probe) BEFORE M9 — per orchestrator cross-lane law 1 the
wifi-off battery must be the LAST move, gated on an inbox ask + Noam's reply.

## M10 — agent-offload probe (stretch, run before M9 per cross-lane ordering)

`curl http://127.0.0.1:11434/v1/chat/completions` with the mission's exact classification
prompt on `qwen3:30b-a3b` → valid OpenAI-shaped JSON (`chat.completion`, choices/message/usage
all present). `message.content` = **"POSITIVE"** — exactly one word, a correct read of the
mixed-sentiment sentence. The `<think>` watch item did NOT fire: Ollama 0.31.1 routes the
hybrid tag's thinking into a separate `reasoning` field, so content stays clean — no
`think:false` retry, no instruct-2507 variant needed. Combined with M5's measured 69.4 tok/s
(bar 35):

**VERDICT: haiku-tier offload VIABLE — wire `http://127.0.0.1:11434/v1` as an OpenAI-compatible
endpoint for mechanical tasks (model `qwen3:30b-a3b`).** One cost note: thinking tokens make
even a one-word answer spend ~500 completion tokens (~7s); for latency-sensitive mechanical
calls, disable thinking via `/api/chat` `"think": false` or accept the overhead.
