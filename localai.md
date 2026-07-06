WARGAME ORDER. You are not executing this mission, you are wargaming it. A cheaper executor (Claude Code on a cheaper model) runs the brief below later. Your job is the route it will follow.

Recon first, read-only: the machine specs below, and the current releases of every tool you plan to recommend. `RECON-SEED.md` in this folder carries pre-settled facts (hardware, installed tools, use cases) and Jan-2026-cutoff model-landscape notes — trust the machine facts, WEB-VERIFY the model/tool facts before recommending anything.

Then fight the mission on paper, move by move, and write it to `~/Claude/localai/wargames/00-localai-stack.md`:

- every move states its expected observation, exactly what you should see if it worked
- every move carries its most likely failure, the cause it signals, and the counter-move
- every fork gets a trigger, if you observe X, take route B
- assumptions recon could not settle get marked RECON NEEDED with the exact check that settles it
- end with abort conditions, and the verification runs the executor must perform with what pass looks like for each

Write it so the executor can run the brief end to end without asking a single question.

RIGHT-SIZING (Fable verdict 2026-07-06, keeps this from being "too serious"): this target is a
LOW-RISK, reversible, single-machine install — apply the wargame move/observation/fork discipline
above, but SKIP the heavy loops the multi-writer live-system wargames needed: no red-team agent
waves, no executor-sim gate, no style bible. One wargame file + one fresh-verifier pass at the end
is the whole apparatus. If you find yourself writing a second mission file, stop and justify it.

=== THE MISSION BRIEF (the executor's orders, not yours) ===

I want a fully local, open source AI setup on this machine, private by default, nothing leaves the box. My hardware: macOS 26.4 (build 25E246), Apple M5 Pro, 18-core CPU / 20-core GPU, 48 GB unified memory, ~803 GB free disk (16-inch MacBook Pro). I'll use it for: private doc chat over my Obsidian vaults + Second Brain (needs embeddings/RAG), coding help, first drafts in BOTH English and Hebrew (Hebrew quality must be explicitly tested, not assumed), and — stretch goal — offloading cheap-mechanical agent tasks that today burn paid API tokens. My patience for tinkering: MEDIUM (I'm a dev, but I want it working, not a hobby).

Set up the stack that fits THIS machine, not a generic tutorial. Note: Ollama 0.30.11 is ALREADY installed (server currently not running) and qwen3:30b-a3b is ALREADY pulled — build on that, don't reinstall blind. Pick the runtime and justify it against my patience level. Pick the exact models with the exact quantizations that fit my memory, one daily driver, one small fast fallback, plus an embedding model for the vault chat (must handle Hebrew — test it). Configure context length (my doc chat needs 16-32k, not the default) and GPU offload for my hardware.

Verify the whole thing end to end. A test prompt runs on each model with tokens per second measured, each of my use cases gets exercised once (including one Hebrew draft and one vault-document Q&A), and confirm nothing phones home — the setup works with wifi off.

Everything must be free and open source (this DISQUALIFIES closed-but-free GUIs — check each tool's license, not its price tag). If my hardware cannot run a good daily driver, say so plainly and name the smallest upgrade that changes that.
