# ChatGPT–Claude collaboration workspace: Brauns family NFL pool

**Objective.** A usable production system, as fast as possible, that maximizes Ryan's probability
of finishing first in the Brauns family NFL straight-up pool. No prose polishing, no laboratory
features that do not move that number.

## Files and who writes them

| File | Written by | Purpose |
|---|---|---|
| `CHATGPT_TO_CLAUDE.md` | ChatGPT (via Ryan pasting a block) | ChatGPT's reviews, reproductions, requests. Newest block at the top, dated. |
| `CLAUDE_TO_CHATGPT.md` | Claude | Claude's substantive responses. Newest block at the top, dated. |
| `DECISIONS.md` | Claude, after review | Short authoritative record of conclusions that survived review, plus the unresolved list with the conservative production choice in force. |
| `RESPONSE.md`, `CRITIQUE.md` | Claude | Long-form analysis already delivered; reference only. |

ChatGPT reads this branch directly but cannot write. Ryan pastes ChatGPT's compact block into
this chat; Claude inserts it verbatim into `CHATGPT_TO_CLAUDE.md`.

## Protocol

1. Before any further model work, Claude reads new material in `CHATGPT_TO_CLAUDE.md`.
2. Claude answers in `CLAUDE_TO_CHATGPT.md`, not in chat.
3. **Two rounds per disagreement, maximum.** Round 1: argument or reproduction. Round 2: response
   or refutation. Then either the result goes into `DECISIONS.md` as settled, or it is marked
   unresolved there and the conservative production choice is used. No further debate unless Ryan
   asks.
4. Engine A (NFL win probabilities) and Engine B (pool strategy) stay separate modules with
   separate logs. Nothing about the family ever touches Engine A.
5. Logs are append-only: `predictions_log.csv`, `engine_b_log.csv`, `pool_picks.csv`. Re-runs
   append rows with new timestamps. Nothing is edited after a result is known.

## Roster (2025–2026 active competitors, N = 7)

Ryan, Casey, Sue, Nolan, Sheila, Kaleigh, Molly.

**R C B is a historical entry belonging to Ryan's late father.** It is excluded from opponent
modeling, active-member counts, simulations and recommendations. It is not an alias for Ryan.

## Running the system

```
python3 nfl-pool/v01_picks.py --season 2026 --week N          # Engine A: market picks + log
python3 nfl-pool/engine_b.py  --season 2026 --week N          # Engine B: recommendation + log
python3 nfl-pool/engine_b.py  --season 2026 --week N --standings standings.json
python3 nfl-pool/engine_b.py  --season 2026 --week N --screen # v1.0 weekly screen with confidence
python3 nfl-pool/engine_b.py  --season 2026 --week N --fit    # refit family.json from pool_picks.csv
python3 nfl-pool/fit_from_scores.py --scores nfl-pool/weekly_scores.csv --season 2025 --write
```

Both accept `--games-file games.csv` to use a local copy of nflverse's game file. Engine B
requires numpy.

## Definition of v1.0 and status

1. Engine B configured for the actual seven-person pool — **done** (`family.json`, biases per D11,
   deviation rates fitted from 2024 weekly scores per D14).
2. Tie rule — **settled as ties-split approximation** (U1).
3. One-screen weekly recommendation — **done** (`engine_b.py --screen`).
**v1.0 reached 2026-09-09.** Production rule: the favorite in every game, playoffs included (D6, D16). Play the season.

## Weekly routine during the season

1. Before the first deadline of the week: `engine_b.py --season 2026 --week N --screen`
   (with `--standings standings.json` from week 2 on). Enter the picks on CBS.
2. After kickoff: record everyone's picks in `pool_picks.csv` (`season, week, game_id, member,
   pick, entered_at`) and the week's points in `weekly_scores.csv`. Update `standings.json`.
3. Every few weeks: `engine_b.py --fit` (uses `pool_picks.csv`) to sharpen `family.json`.
