#!/usr/bin/env python3
"""Estimate each member's underdog-pick RATE from weekly pool scores alone. It never infers which
games anyone picked; it uses only how far each member's weekly score wandered from the all-favorites
score, which is a function of how often they deviated.

    python3 fit_from_scores.py --scores weekly_scores.csv --season 2025 [--games-file games.csv]
                               [--family family.json] [--write]

weekly_scores.csv columns:  season, week, member, points        (points = correct picks that week)
Optional column:            games_picked   (if a member skipped games; weeks with points < 50% of the
                            chalk score are dropped as likely missed weeks)

Model. Chalk score C_w = number of games in week w won by the no-vig favorite (home team on a dead
heat). A member who deviates in a set of games J has weekly difference D = sum_j (1 - 2*favwin_j),
so E[D] = -sum_j (2p_j - 1) and E[D^2] = |J| + (sum_j (1 - 2p_j))^2. With deviations occurring at
rate r in close games (favorite < 62%) the season-average second moment is
    E[D^2] ~= r * n_close + r^2 * (sum_close (1 - 2p_j))^2
solved for r per member (method of moments), then shrunk toward the prior in family.json with
weight PRIOR_WEEKS. Bands: tossup rate = 1.3 r, close = 0.8 r, other = 0.15 r (a fixed shape;
scores cannot identify the shape, only the level).
Output: proposed dog_rate per member; --write updates family.json. Bias fields are left untouched.
"""
import argparse, csv, io, json, math, os, urllib.request
from collections import defaultdict

URL = "https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv"
HERE = os.path.dirname(os.path.abspath(__file__))
PRIOR_WEEKS = 6.0

def american_to_prob(ml):
    ml = float(ml); return 100 / (ml + 100) if ml > 0 else -ml / (-ml + 100)

def week_lines(games, season):
    """week -> list of (p_fav, fav_won) for completed REG games with moneylines."""
    out = defaultdict(list)
    for g in games:
        if int(g["season"]) != season or g["game_type"] != "REG" or g["result"] == "": continue
        if not (g["away_moneyline"] and g["home_moneyline"]): continue
        pa, ph = american_to_prob(g["away_moneyline"]), american_to_prob(g["home_moneyline"]); ph = ph / (pa + ph)
        res = float(g["result"]); fav_home = ph >= 0.5
        fav_won = (res > 0) if fav_home else (res < 0)     # a tie counts as a loss for the favorite (CBS: no point)
        out[int(g["week"])].append((max(ph, 1 - ph), fav_won))
    return out

def estimate_rate(diffs_by_week, lines):
    """diffs_by_week: {week: D}. Solve r^2*B + r*A - M = 0 where M = mean D^2."""
    weeks = sorted(diffs_by_week); A = B = M = 0.0
    for w in weeks:
        close = [(p, f) for p, f in lines[w] if p < 0.62]
        n = len(close); s = sum(1 - 2 * p for p, _ in close)
        A += n; B += s * s; M += diffs_by_week[w] ** 2
    A /= len(weeks); B /= len(weeks); M /= len(weeks)
    if B < 1e-9: return M / A if A else 0.0
    return max(0.0, (-A + math.sqrt(A * A + 4 * B * M)) / (2 * B))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True); ap.add_argument("--season", type=int, required=True)
    ap.add_argument("--games-file"); ap.add_argument("--family", default=os.path.join(HERE, "family.json"))
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    games = list(csv.DictReader(open(a.games_file, newline=""))) if a.games_file else \
            list(csv.DictReader(io.StringIO(urllib.request.urlopen(URL).read().decode())))
    lines = week_lines(games, a.season)
    chalk = {w: sum(f for _, f in v) for w, v in lines.items()}
    rows = [r for r in csv.DictReader(open(a.scores, newline="")) if int(r["season"]) == a.season]
    family = json.load(open(a.family)) if os.path.exists(a.family) else []
    names = {m["name"]: m for m in family}
    by_member = defaultdict(dict); dropped = []
    for r in rows:
        w = int(r["week"]); pts = float(r["points"])
        if w not in chalk: continue
        if pts < 0.5 * chalk[w]: dropped.append((r["member"], w)); continue
        by_member[r["member"]][w] = pts - chalk[w]
    if dropped: print("dropped as probable missed weeks:", dropped)
    print(f"season {a.season}: chalk score by week = { {w: chalk[w] for w in sorted(chalk)} }")
    print(f"\n{'member':10} {'weeks':>5} {'meanD':>6} {'sdD':>5} {'r_raw':>6} {'r_shrunk':>8}  {'-> dog_rate (tossup/close/other)':>34}")
    for name in sorted(by_member):
        d = by_member[name]; n = len(d); vals = list(d.values())
        mean = sum(vals) / n; sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / max(1, n - 1))
        r_raw = estimate_rate(d, lines)
        prior = names.get(name, {}).get("dog_rate", {}).get("close", 0.07) / 0.8
        r = (r_raw * n + prior * PRIOR_WEEKS) / (n + PRIOR_WEEKS)
        rates = {"tossup": round(min(0.9, 1.3 * r), 3), "close": round(min(0.9, 0.8 * r), 3), "other": round(0.15 * r, 3)}
        flag = "" if name in names else "  (not in family.json; ignored on --write)"
        print(f"{name:10} {n:5d} {mean:+6.2f} {sd:5.2f} {r_raw:6.3f} {r:8.3f}  {rates['tossup']:.3f}/{rates['close']:.3f}/{rates['other']:.3f}{flag}")
        if a.write and name in names: names[name]["dog_rate"] = rates
    if a.write:
        json.dump(family, open(a.family, "w"), indent=1); print(f"\nwrote {a.family}")

if __name__ == "__main__":
    main()
