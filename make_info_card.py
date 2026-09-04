#!/usr/bin/env python3
"""
make_info_card.py

Generates info-card.svg — a neofetch-style panel that fades/slides in
line by line. Pure SVG + CSS keyframes, no JS, so it plays fine inside
a GitHub-rendered <img> tag.

Usage:
    python scripts/make_info_card.py            # animated version
    STATIC=1 python scripts/make_info_card.py    # frozen frame (for local previews)
"""
import os

WIDTH, HEIGHT = 490, 300
BG = "#0d1117"
BORDER = "#30363d"
TITLE = "#58a6ff"
LABEL = "#7ee787"
TEXT = "#c9d1d9"
DIM = "#8b949e"

# (label, value) rows shown neofetch-style
ROWS = [
    ("OS", "Computer Science & Technology"),
    ("Role", "Full Stack + Python Developer"),
    ("Stack", "React · Node · Django REST · Mongo"),
    ("Learning", "System Design · ML · Cloud"),
    ("Projects", "WealthNest · SpendWise · CareeRise"),
    ("Looking for", "SWE Internships · Python/MERN roles"),
    ("Fun fact", "Sings as much as she ships code"),
]

STATIC = os.environ.get("STATIC") == "1"

ROW_H = 26
TOP_PAD = 66
STAGGER = 0.12  # seconds between each row's entrance


def row_svg(i, label, value):
    y = TOP_PAD + i * ROW_H
    delay = i * STAGGER
    group_style = "" if STATIC else (
        f'style="opacity:0;animation:rowIn .5s ease-out forwards;'
        f'animation-delay:{delay:.2f}s"'
    )
    return f'''
  <g {group_style}>
    <text x="28" y="{y}" font-family="'JetBrains Mono','Fira Code',monospace"
          font-size="14" font-weight="600" fill="{LABEL}">{label}</text>
    <text x="180" y="{y}" font-family="'JetBrains Mono','Fira Code',monospace"
          font-size="14" fill="{TEXT}">{value}</text>
  </g>'''


def build_svg():
    rows = "".join(row_svg(i, l, v) for i, (l, v) in enumerate(ROWS))
    caret_style = "" if STATIC else (
        'style="animation:blink 1s steps(2) infinite;"'
    )
    keyframes = "" if STATIC else '''
    <style>
      @keyframes rowIn {
        from { opacity: 0; transform: translateX(-8px); }
        to   { opacity: 1; transform: translateX(0); }
      }
      @keyframes blink {
        50% { opacity: 0; }
      }
    </style>'''

    return f'''<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}"
     xmlns="http://www.w3.org/2000/svg">
  {keyframes}
  <rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="10"
        fill="{BG}" stroke="{BORDER}"/>

  <!-- title bar -->
  <circle cx="24" cy="24" r="6" fill="#ff5f56"/>
  <circle cx="44" cy="24" r="6" fill="#ffbd2e"/>
  <circle cx="64" cy="24" r="6" fill="#27c93f"/>
  <text x="{WIDTH/2}" y="29" text-anchor="middle" font-family="'JetBrains Mono',monospace"
        font-size="13" fill="{DIM}">shreeya@github</text>
  <line x1="0" y1="42" x2="{WIDTH}" y2="42" stroke="{BORDER}"/>

  <text x="28" y="{TOP_PAD - 18}" font-family="'JetBrains Mono',monospace"
        font-size="14" fill="{TITLE}">shreeya@github <tspan fill="{TEXT}">~ $</tspan> whoami<tspan {caret_style}>_</tspan></text>

  {rows}
</svg>'''


if __name__ == "__main__":
    svg = build_svg()
    out_path = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"wrote {out_path}")
