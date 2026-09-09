#!/usr/bin/env python3
"""ENGINE B: family-pool optimizer. Chooses picks to maximize P(finish first), not expected score.

    python3 engine_b.py --season 2026 --week 1 [--standings standings.json] [--family family.json]
                        [--sims 20000] [--games-file games.csv] [--dry-run]

Inputs
  games.csv (nflverse)      remaining schedule; win probabilities from no-vig moneylines where present,
                            else from the spread (logistic on spread/13.5), else 0.57 for the home team.
  family.json               opponent pick model, one entry per opponent:
                              {"name": "Sue", "dog_rate": {"tossup": 0.30, "close": 0.10, "other": 0.02},
                               "bias_team": "GB", "bias_strength": 0.5}
                            dog_rate = P(picks the underdog) by favorite-probability band
                            (tossup: fav<55%, close: 55-62%, other: >=62%). bias_strength = P(picks the
                            bias team regardless of the line) when that team plays.
  standings.json            {"Ryan": 12, "Sue": 13, ...} points so far (omit in week 1).
Method
  Monte Carlo with common random numbers. For every game this week, compare P(first) when the user picks
  the favorite vs the dog, holding the other current-week picks at the current policy; two coordinate
  passes so multiple deviations are evaluated jointly. Future-week user picks are assumed to follow the
  same rule that is being evaluated in the current week (dog only when favorite < 52%, otherwise favorite).
  Recommendations are appended to engine_b_log.csv (append-only) with a timestamp.
Everything about the opponents is an ASSUMPTION until pool_picks.csv has data; --fit updates family.json
from pool_picks.csv with a Beta(2,8)-style shrinkage prior on each rate.
"""
import argparse, csv, datetime as dt, io, json, math, os, urllib.request
import numpy as np

URL = "https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv"
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FAMILY = [
    {"name": "Sue", "dog_rate": {"tossup": 0.30, "close": 0.15, "other": 0.03}, "bias_team": "GB", "bias_strength": 0.5},
    {"name": "Nolan", "dog_rate": {"tossup": 0.40, "close": 0.25, "other": 0.08}, "bias_team": "CHI", "bias_strength": 0.5},
    {"name": "Mom", "dog_rate": {"tossup": 0.25, "close": 0.10, "other": 0.03}, "bias_team": "CHI", "bias_strength": 0.6},
    {"name": "Daughter", "dog_rate": {"tossup": 0.30, "close": 0.15, "other": 0.05}, "bias_team": "GB", "bias_strength": 0.6},
    {"name": "Other", "dog_rate": {"tossup": 0.25, "close": 0.10, "other": 0.03}, "bias_team": None, "bias_strength": 0.0},
]
USER_DOG_THRESHOLD = 0.52   # default future-week policy for the user

def american_to_prob(ml):
    ml = float(ml); return 100 / (ml + 100) if ml > 0 else -ml / (-ml + 100)

def home_prob(g):
    if g["away_moneyline"] and g["home_moneyline"]:
        pa, ph = american_to_prob(g["away_moneyline"]), american_to_prob(g["home_moneyline"])
        return ph / (pa + ph)
    if g["spread_line"]:
        return 1 / (1 + math.exp(-float(g["spread_line"]) / 13.5 * 1.6))
    return 0.57

def load_games(path):
    return list(csv.DictReader(open(path, newline=""))) if path else \
           list(csv.DictReader(io.StringIO(urllib.request.urlopen(URL).read().decode())))

def band(pfav): return "tossup" if pfav < 0.55 else "close" if pfav < 0.62 else "other"

def opponent_pick_fav_prob(member, g, pfav, fav_team):
    """P(member picks the favorite) for game g."""
    base = 1 - member["dog_rate"][band(pfav)]
    bt = member.get("bias_team")
    if bt and bt in (g["home_team"], g["away_team"]):
        s = member.get("bias_strength", 0.0)
        return s * (1.0 if fav_team == bt else 0.0) + (1 - s) * base
    return base

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", type=int, required=True); ap.add_argument("--week", type=int, required=True)
    ap.add_argument("--games-file"); ap.add_argument("--family", default=os.path.join(HERE, "family.json"))
    ap.add_argument("--standings"); ap.add_argument("--sims", type=int, default=20000)
    ap.add_argument("--user", default="Ryan"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fit", action="store_true", help="update family.json from pool_picks.csv, then exit")
    a = ap.parse_args()

    family = json.load(open(a.family)) if os.path.exists(a.family) else DEFAULT_FAMILY
    if a.fit:
        return fit_family(a, family)
    standings = json.load(open(a.standings)) if a.standings else {}
    games = [g for g in load_games(a.games_file) if int(g["season"]) == a.season and g["game_type"] == "REG"
             and int(g["week"]) >= a.week and g["result"] == ""]
    games.sort(key=lambda g: (int(g["week"]), g["gameday"]))
    G = len(games); N = len(family)
    ph = np.array([home_prob(g) for g in games]); pfav = np.maximum(ph, 1 - ph)
    fav_home = ph >= 0.5
    this_week = np.array([int(g["week"]) == a.week for g in games])
    fav_team = [g["home_team"] if fh else g["away_team"] for g, fh in zip(games, fav_home)]
    # opponent pick-favorite probabilities (G, N)
    P_opp = np.array([[opponent_pick_fav_prob(m, g, pf, ft) for m in family] for g, pf, ft in zip(games, pfav, fav_team)])
    rng = np.random.default_rng(a.season * 100 + a.week)
    S = a.sims
    fav_wins = rng.random((S, G)) < pfav[None, :]
    opp_fav = rng.random((S, G, N)) < P_opp[None, :, :]
    opp_pts = np.array([standings.get(m["name"], 0) for m in family], float)
    user_pts = float(standings.get(a.user, 0))
    opp_scores = opp_pts[None, :] + (opp_fav == fav_wins[:, :, None]).sum(1)  # (S,N)

    user_fav = pfav >= USER_DOG_THRESHOLD   # default policy, evaluated jointly below
    def p_first(uf):
        us = user_pts + (uf[None, :] == fav_wins).sum(1)
        best = np.maximum(us, opp_scores.max(1)); ntop = (opp_scores == best[:, None]).sum(1) + (us == best)
        return np.where(us == best, 1.0 / ntop, 0.0).mean()
    base = p_first(user_fav)
    idx = np.where(this_week)[0]
    deltas = {}
    for _ in range(2):  # coordinate passes
        for i in idx:
            u1 = user_fav.copy(); u1[i] = True; u0 = user_fav.copy(); u0[i] = False
            pf_, pd_ = p_first(u1), p_first(u0)
            deltas[i] = pd_ - pf_
            user_fav[i] = pf_ >= pd_
    final = p_first(user_fav)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"Engine B  season {a.season} week {a.week}  user={a.user}  sims={S}  opponents={[m['name'] for m in family]}")
    print(f"P(first) all-favorite this week: {base:.3f}   with recommended picks: {final:.3f}\n")
    print(f"{'game':10} {'fav':>4} {'P(fav)':>7} {'oppFav%':>8} {'dP(first) if dog':>17}  pick")
    out = []
    for i in idx:
        g = games[i]; pick = fav_team[i] if user_fav[i] else (g["away_team"] if fav_home[i] else g["home_team"])
        print(f"{g['away_team']+'@'+g['home_team']:10} {fav_team[i]:>4} {pfav[i]:7.3f} {P_opp[i].mean():8.2f} {deltas[i]:+17.4f}  {pick}")
        out.append(dict(logged_at_utc=now, season=a.season, week=a.week, game_id=g["game_id"], fav=fav_team[i],
                        p_fav=f"{pfav[i]:.4f}", opp_fav_rate=f"{P_opp[i].mean():.3f}", dP_first_dog=f"{deltas[i]:+.4f}",
                        recommendation=pick, p_first_base=f"{base:.4f}", p_first_final=f"{final:.4f}",
                        standings=json.dumps(standings) if standings else "", family_model=os.path.basename(a.family)))
    if not a.dry_run:
        log = os.path.join(HERE, "engine_b_log.csv"); new = not os.path.exists(log)
        with open(log, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader() if new else None; w.writerows(out)
        print(f"\nappended {len(out)} rows to {log}")

def fit_family(a, family):
    """Beta-shrunk dog rates by band from pool_picks.csv (columns: season,week,game_id,member,pick)."""
    picks_path = os.path.join(HERE, "pool_picks.csv")
    if not os.path.exists(picks_path):
        print("no pool_picks.csv yet; family.json left as priors"); return
    games = {g["game_id"]: g for g in load_games(a.games_file)}
    counts = {m["name"]: {b: [0, 0] for b in ("tossup", "close", "other")} for m in family}
    for r in csv.DictReader(open(picks_path, newline="")):
        g = games.get(r["game_id"]);
        if not g or r["member"] not in counts: continue
        p = home_prob(g); pf = max(p, 1 - p); fav = g["home_team"] if p >= 0.5 else g["away_team"]
        c = counts[r["member"]][band(pf)]; c[0] += 1; c[1] += (r["pick"] != fav)
    prior_n = 10.0
    for m in family:
        for b in ("tossup", "close", "other"):
            n, d = counts[m["name"]][b]; prior = m["dog_rate"][b]
            m["dog_rate"][b] = round((d + prior * prior_n) / (n + prior_n), 3)
    json.dump(family, open(a.family, "w"), indent=1)
    print("family.json updated with shrinkage (prior weight = 10 picks per band)")

if __name__ == "__main__":
    main()
