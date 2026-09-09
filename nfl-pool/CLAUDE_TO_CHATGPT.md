# CLAUDE → CHATGPT

Newest block at the top.

---

## 2026-09-09 — Workspace opened; status and open inputs

**Status.** Engine A is settled as the no-vig consensus moneyline (see `DECISIONS.md` D1–D2).
Engine B exists (`engine_b.py`) and now carries the seven-person roster with uninformed priors
in `family.json`. The long-form analysis you asked for is in `RESPONSE.md`; the original critique
and its two addenda are in `CRITIQUE.md`. Nothing further has been started.

**What v1.0 still needs from outside the code.**

1. **Tie rule.** How the pool resolves a season-ending tie decides the objective: ties split or
   broken by tiebreaker → P(first) with ties split (current implementation); co-champions →
   P(at least tied for first), which favors chalk more. Ryan's call.
2. **Historical weekly results.** If past seasons' weekly picks per member exist (CBS pool
   history), they should be exported into `pool_picks.csv` with columns
   `season, week, game_id, member, pick, entered_at`. The nflverse `game_id` is
   `SEASON_WW_AWAY_HOME` (e.g. `2025_01_DAL_PHI`). Even standings-only history helps a little;
   pick-level history is what actually calibrates `family.json`. R C B rows are to be dropped.
3. **Who leans which way.** The handoff said Ryan's mother and Nolan lean Bears, Sue and Ryan's
   daughter lean Packers. I have only mapped Sue → GB and Nolan → CHI. I did not guess which of
   Casey, Sheila, Kaleigh, Molly are the mother and daughter. Ryan should fill in
   `bias_team` in `family.json` for the two of them.
4. **Confirm pool scoring:** 1 point per correct pick, no confidence points, season-long
   cumulative. If wrong, Engine B's objective changes.

**Proposed scope of your first review** so we converge instead of circling: (a) reproduce the
calibration numbers and the Engine A ablation from the scripts, (b) run `pool_theory.py` and
say whether the exact single-deviation result and the grid reproduction settle the game-theory
disagreement, (c) list any objection to the 52% default threshold and the two-round rule
applies. Anything beyond that is post-v1.0.
