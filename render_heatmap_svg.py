#!/usr/bin/env python3
"""
render_heatmap_svg.py

Reads data/contributions.json and draws the classic 53-week x 7-day
contribution calendar as rounded boxes that slide in diagonally on
load, then freeze. CSS keyframes only -- no JS.
"""
import json
import os
from collections import defaultdict
from datetime import datetime

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

BOX = 11
GAP = 3
CELL = BOX + GAP
LEFT_PAD = 34
TOP_PAD = 34
BOTTOM_PAD = 46
STAGGER = 0.006  # seconds per (week+day) step -> keeps total anim under ~1s


def load_data():
    in_path = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
    with open(in_path) as f:
        return json.load(f)


def to_weeks(days):
    """Bucket the flat day list into 53 columns of 7 (Sun-Sat)."""
    by_date = {d["date"]: d for d in days}
    if not days:
        return []
    dates = sorted(by_date)
    start = datetime.strptime(dates[0], "%Y-%m-%d")
    # rewind to the preceding Sunday so columns align to calendar weeks
    start = start.fromordinal(start.toordinal() - start.weekday() - 1) if start.weekday() != 6 else start

    weeks = []
    cur_week = []
    cursor = start
    end = datetime.strptime(dates[-1], "%Y-%m-%d")
    while cursor <= end:
        key = cursor.strftime("%Y-%m-%d")
        cur_week.append(by_date.get(key, {"date": key, "level": 0, "count": 0}))
        if len(cur_week) == 7:
            weeks.append(cur_week)
            cur_week = []
        cursor = cursor.fromordinal(cursor.toordinal() + 1)
    if cur_week:
        weeks.append(cur_week)
    return weeks


def build_svg(payload, static=False):
    weeks = to_weeks(payload["days"])
    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * CELL + 20
    height = TOP_PAD + 7 * CELL + BOTTOM_PAD

    cells = []
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            level = max(0, min(5, day.get("level", 0)))
            color = PALETTE[level]
            x = LEFT_PAD + wi * CELL
            y = TOP_PAD + di * CELL
            delay = (wi + di) * STAGGER
            style = "" if static else (
                f'style="opacity:0;transform:translate(-6px,-6px);'
                f'animation:slideIn .4s ease-out forwards;animation-delay:{delay:.3f}s"'
            )
            cells.append(
                f'<rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2" '
                f'fill="{color}" {style}><title>{day["date"]}: {day.get("count") or 0} contributions</title></rect>'
            )

    legend_x = width - 150
    legend_y = height - 16
    legend = [f'<text x="{legend_x-34}" y="{legend_y+8}" font-family="monospace" font-size="10" fill="#8b949e">Less</text>']
    for i, color in enumerate(PALETTE):
        legend.append(f'<rect x="{legend_x + i*14}" y="{legend_y}" width="{BOX}" height="{BOX}" rx="2" fill="{color}"/>')
    legend.append(f'<text x="{legend_x + len(PALETTE)*14 + 6}" y="{legend_y+8}" font-family="monospace" font-size="10" fill="#8b949e">More</text>')

    stats = payload.get("stats", {})
    footer = (
        f'{stats.get("total_last_year", "?")} contributions in the last year · '
        f'current streak {stats.get("current_streak", "?")}d · '
        f'longest streak {stats.get("longest_streak", "?")}d'
    )

    keyframes = "" if static else '''
  <style>
    @keyframes slideIn {
      to { opacity: 1; transform: translate(0,0); }
    }
  </style>'''

    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     xmlns="http://www.w3.org/2000/svg">
  {keyframes}
  <rect x="0" y="0" width="{width}" height="{height}" fill="#0d1117"/>
  <text x="{LEFT_PAD}" y="20" font-family="monospace" font-size="12" fill="#c9d1d9">{payload.get("username","")}'s contributions</text>
  {''.join(cells)}
  {''.join(legend)}
  <text x="{LEFT_PAD}" y="{height-6}" font-family="monospace" font-size="11" fill="#8b949e">{footer}</text>
</svg>'''


def main():
    payload = load_data()
    static = os.environ.get("STATIC") == "1"
    svg = build_svg(payload, static=static)
    out_path = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
