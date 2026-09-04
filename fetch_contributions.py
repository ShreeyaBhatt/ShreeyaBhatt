#!/usr/bin/env python3
"""
fetch_contributions.py

Pulls the public contribution calendar from
https://github.com/users/<username>/contributions
(the same HTML fragment the profile page itself uses) and writes
data/contributions.json with raw days + a few derived stats.

No GraphQL API, no personal access token required.
"""
import json
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_PROFILE_USER", "ShreeyaBhatt")
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-art-bot"}, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    for cell in soup.select("td.ContributionCalendar-day, rect.ContributionCalendar-day"):
        date = cell.get("data-date")
        if not date:
            continue
        level = cell.get("data-level")
        if level is None:
            # older markup encodes level in a class like "ContributionCalendar-day--4"
            m = re.search(r"--(\d)", " ".join(cell.get("class", [])))
            level = m.group(1) if m else "0"
        count_attr = cell.get("data-count")
        days.append({
            "date": date,
            "level": int(level),
            "count": int(count_attr) if count_attr else None,
        })

    days.sort(key=lambda d: d["date"])
    return days


def derive_stats(days):
    total = sum(d["count"] or 0 for d in days if d["count"] is not None)
    # current streak: consecutive days (from the end) with count > 0
    streak = 0
    for d in reversed(days):
        if (d["count"] or 0) > 0:
            streak += 1
        else:
            break
    longest = cur = 0
    for d in days:
        if (d["count"] or 0) > 0:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0
    best_day = max(days, key=lambda d: d["count"] or 0) if days else None
    return {
        "total_last_year": total,
        "current_streak": streak,
        "longest_streak": longest,
        "best_day": best_day["date"] if best_day else None,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def main():
    days = fetch_days()
    payload = {"username": USERNAME, "days": days, "stats": derive_stats(days)}
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"wrote {len(days)} days -> {out_path}")


if __name__ == "__main__":
    main()
