"""
Render the "about me + tech stack" panel as an animated terminal-window SVG that
sits beside stats.svg (same 840x1220 canvas, same palette). Lines slide in one
by one, then the skill icons pop in. Icons come from skillicons.dev and are
embedded as data URIs, because GitHub's <img> sandbox blocks external fetches.
"""
import base64
import os
import sys

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "about.svg")

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#e6edf3"
GREEN = "#39d353"

W, H = 840, 1220                     # == stats.svg canvas
PAD = 20
TITLEBAR_H = 30
X0 = PAD + 24
LINE_H = 40
ICON, ICON_GAP, PER_ROW = 120, 22, 4

ABOUT = [
    ("🎨", ["Frontend developer who turns designs", "into pixel-perfect, responsive UIs"]),
    ("⚛️", ["Crafting fast, modern apps with React,", "Next.js, TypeScript & Tailwind CSS"]),
    ("✨", ["Obsessed with smooth animations, clean", "components, and great UX"]),
    ("📍", ["State Polytechnic of Jember"]),
]
STACKS = [
    ("ls ./frontend", ["ts", "js", "react", "nextjs", "tailwind", "html", "css"]),
    ("ls ./backend", ["php", "laravel", "postgres", "nestjs", "python", "docker"]),
]

# timing (seconds)
STEP = 0.12
SLIDE = 0.45
POP = 0.4


def icon_uri(name):
    svg = requests.get(f"https://skillicons.dev/icons?i={name}&theme=dark", timeout=30).content
    return "data:image/svg+xml;base64," + base64.b64encode(svg).decode()


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
    f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<style>'
    f'.t{{opacity:0;animation:in {SLIDE}s ease-out both}}'
    '@keyframes in{0%{opacity:0;transform:translateX(-16px)}100%{opacity:1;transform:translateX(0)}}'
    f'.p{{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop {POP}s cubic-bezier(.34,1.56,.64,1) both}}'
    '@keyframes pop{0%{opacity:0;transform:scale(.3)}100%{opacity:1;transform:scale(1)}}'
    '.c{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}'
    '@media (prefers-reduced-motion: reduce){.t,.p{opacity:1!important;transform:none!important;animation:none!important}}'
    '</style>',
    f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">krisna@github: ~$ cat about.md</text>')

t = 0.0
y = TITLEBAR_H + 70


def line(text, x, y, size, fill, weight="normal"):
    global t
    parts.append(f'<text class="t" xml:space="preserve" style="animation-delay:{t:.2f}s" x="{x}" y="{y}" '
                 f'fill="{fill}" font-size="{size}" font-weight="{weight}">{text}</text>')
    t += STEP


line(f'<tspan fill="{GREEN}">$</tspan> whoami', X0, y, 28, INK, "bold")
y += 56
for emoji, rows in ABOUT:
    for k, row in enumerate(rows):
        lead = f'{emoji} ' if k == 0 else '   '
        line(esc(lead + row), X0, y, 24, INK)
        y += LINE_H
    y += 8

for cmd, icons in STACKS:
    y += 40
    line(f'<tspan fill="{GREEN}">$</tspan> {cmd}', X0, y, 28, INK, "bold")
    y += 24
    for i, name in enumerate(icons):
        col, row = i % PER_ROW, i // PER_ROW
        ix = X0 + col * (ICON + ICON_GAP)
        iy = y + row * (ICON + ICON_GAP)
        parts.append(f'<image class="p" style="animation-delay:{t:.2f}s" x="{ix}" y="{iy}" '
                     f'width="{ICON}" height="{ICON}" href="{icon_uri(name)}"/>')
        t += STEP / 2
    rows_n = (len(icons) + PER_ROW - 1) // PER_ROW
    y += rows_n * ICON + (rows_n - 1) * ICON_GAP

# blinking prompt at the bottom
y += 70
parts.append(f'<text class="t" style="animation-delay:{t:.2f}s" x="{X0}" y="{y}" fill="{INK}" font-size="28" '
             f'font-weight="bold"><tspan fill="{GREEN}">$</tspan> <tspan class="c">▋</tspan></text>')

parts.append('</svg>')
svg = "\n".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {OUT}: {W} x {H}, content ends at y={y}, {len(svg)//1024} KB")
