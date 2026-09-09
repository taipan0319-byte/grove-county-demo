# DECISIONS — authoritative record

Entries here survived review. Anything not listed is open. Format: ID, decision, basis, date.

## Settled

- **D1. Engine A production probability = no-vig consensus moneyline.** Basis: 4,842 games
  2007–2025, calibration within 2.4 points in every bucket (`backtest_market.py`). 2026-09-09.
- **D2. No residual football model in production for 2026.** Basis: chronological ablation
  (`engine_a.py`) — Elo, rest, division, weather and QB-change blocks all worsen out-of-sample log
  loss; the model's disagreements with the market win at coin-flip rates. Challenger kept only as a
  test harness. EPA and injury features remain untested (offseason). 2026-09-09.
- **D3. The objective is P(finish first), not expected correct picks.** 2026-09-09.
- **D4. Early-season selective contrarianism can raise P(first).** Claude's original claim that
  dogs only add variance was wrong and is withdrawn. Basis: exact result that one deviation onto a
  q-dog against a fully correlated field gives P(first) = q versus 1/N; simulations in
  `pool_theory.py` and ChatGPT's independent grid agree qualitatively. 2026-09-09.
- **D5. Dog picks in games with a favorite of 55% or more are negative in every scenario tested.**
  The original "Upset Radar" for 60/40 games is retired. 2026-09-09.
- **D6. Production rule until family data exists:** favorite whenever the no-vig favorite is 52%
  or higher; below 52%, whichever side Engine B scores higher under the current `family.json`.
  Conservative choice; revisit after `--fit` has real picks. 2026-09-09.
- **D7. Roster N = 7:** Ryan, Casey, Sue, Nolan, Sheila, Kaleigh, Molly. R C B (Ryan's late father)
  is excluded from everything and is not an alias for Ryan. 2026-09-09.
- **D8. Engines A and B stay separate; logs are append-only.** 2026-09-09.
- **D9. Preseason narratives, joint-practice reports, Opta and expert picks carry zero model weight.**
  2026-09-09.
- **D10. Pool scoring confirmed: 1 point per correct winner, no confidence points, season-long.**
  Source: Ryan via ChatGPT block 1. 2026-09-09.
- **D11. Bias mapping:** Sheila → CHI, Nolan → CHI, Sue → GB, Kaleigh → GB at strength 0.4 (prior);
  Casey and Molly neutral. Source: Ryan. 2026-09-09.
- **D12. Historical individual picks are unavailable; 2025 weekly scores are.** Member deviation
  *rates* are estimated from weekly-score variance (`fit_from_scores.py`); individual selections
  are never inferred. 2026-09-09.
- **D13. Weekly screen and confidence rule.** `engine_b.py --screen`; LOW confidence resolves to the
  favorite. 2026-09-09.

## Unresolved (conservative production choice in force)

- **U1. Tie rule.** In force: ties split evenly. Ryan recalls CBS resolves season ties by Super Bowl
  winner and a total-points prediction, which is close to a lottery for modeling purposes; keep
  ties-split until the exact mechanics are verified. Not modeling co-champions.
- **U2. Family deviation rates.** In force: uniform priors (15% toss-ups, 7% close, 2% other) until
  `weekly_scores.csv` for 2025 is supplied and fitted. Bias mapping is now settled (D11); the 0.4
  strength is still a prior.
- **U4. Level differences between ChatGPT's simulation grid and Claude's.** Same shape, different
  levels; cause not identified (probability distribution, tie handling, or where opponent
  deviations land). Does not change any decision. Closed unless it starts to matter.
