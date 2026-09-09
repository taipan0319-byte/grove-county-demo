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
- **D6 (revised). Production rule: the no-vig favorite in every game, including coin flips.**
  Basis: with `family.json` fitted to the 2024 weekly scores, Engine B scores every Week 1 dog
  pick negative at HIGH confidence, including the three games under 53%. The earlier 52%
  threshold assumed a chalk-heavy family; the family is not chalk-heavy. Re-evaluated weekly by
  the screen; the rule changes only if the screen says so. 2026-09-09.
- **D7. Roster N = 7:** Ryan, Casey, Sue, Nolan, Sheila, Kaleigh, Molly. R C B (Ryan's late father)
  is excluded from everything and is not an alias for Ryan. 2026-09-09.
- **D8. Engines A and B stay separate; logs are append-only.** 2026-09-09.
- **D9. Preseason narratives, joint-practice reports, Opta and expert picks carry zero model weight.**
  2026-09-09.
- **D10. Pool scoring confirmed: 1 point per correct winner, no confidence points, season-long.**
  Source: Ryan via ChatGPT block 1. 2026-09-09.
- **D11. Bias mapping:** Sheila → CHI, Nolan → CHI, Sue → GB, Kaleigh → GB at strength 0.4 (prior);
  Casey and Molly neutral. Source: Ryan. 2026-09-09.
- **D12 (amended). Historical individual picks are unavailable; weekly scores are.** The scores Ryan
  supplied are the **2024** season (CBS year selector, and confirmed by matching weekly scores to
  the all-favorites score: week 13 family 12–15 vs 2024 favorites 13/16, 2025 favorites 9/16).
  Weeks 5–18 itemized; weeks 1–4 only as a combined total; playoff weeks excluded. Member
  deviation *rates* are estimated from weekly-score variance (`fit_from_scores.py`); individual
  selections are never inferred. 2026-09-09.
- **D14. The family is not Vegas-heavy; chalk would have won 2024.** All-favorites scored 158 over
  weeks 5–18. Casey 156, Sue 156, Sheila 148, Nolan 142, Ryan 136, Kaleigh 135, Molly 117. The two
  members closest to chalk finished 1st and 2nd. Ryan gave up 22 points to chalk in 14 weeks.
  Fitted close-game underdog rates (shrunk): Sue 0.18, Casey 0.22, Sheila 0.31, Kaleigh 0.45,
  Nolan 0.56, Molly 0.74; Ryan's own 2024 rate 0.71. Rates above ~0.6 mean deviation extends
  beyond close games and may include unpicked games; the effect on Engine B is the same. 2026-09-09.
- **D15. Screen-name mapping (INFERRED, awaiting Ryan's confirmation):** "Don't Be …" is the
  highlighted (logged-in) row → Ryan; "ray rice's …" → Nolan by elimination. Casey, Sue, Sheila,
  Kaleigh, Molly by name. 2026-09-09.
- **D13. Weekly screen and confidence rule.** `engine_b.py --screen`; LOW confidence resolves to the
  favorite. 2026-09-09.

## Unresolved (conservative production choice in force)

- **U1. Tie rule.** In force: ties split evenly. Ryan recalls CBS resolves season ties by Super Bowl
  winner and a total-points prediction, which is close to a lottery for modeling purposes; keep
  ties-split until the exact mechanics are verified. Not modeling co-champions.
- **U2. Family deviation rates.** In force: rates fitted from 2024 scores (D14), 14 weeks each,
  shrunk toward the prior. Bias strength 0.4 remains a prior. Will be refit from 2026 picks in
  `pool_picks.csv` every few weeks. If the CBS year selector also offers 2025, those scores would
  double the sample.
- **U4. Level differences between ChatGPT's simulation grid and Claude's.** Same shape, different
  levels; cause not identified (probability distribution, tie handling, or where opponent
  deviations land). Does not change any decision. Closed unless it starts to matter.
