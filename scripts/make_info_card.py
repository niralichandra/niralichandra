#!/usr/bin/env python3
"""
Author a neofetch-style info card SVG: a terminal title bar, colored key/value rows.
Staggered reveal animation matching the portrait.

    python scripts/make_info_card.py           # writes info-card.svg
    STATIC=1 python scripts/make_info_card.py  # frozen frame for previews
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

USER = "nirali"
HOST = "github"

ROWS = [
    ("Name", "Nirali Chandra"),
    ("Role", "Full-Stack Developer · Unreal Engine Dev · AI Engineer"),
    ("Interests", "Machine Learning, Game Systems, Computer Vision"),
    ("Focus", "Real-Time Systems & Intelligent Web Apps"),
    ("Certs", "Microsoft & Google Certified in Web Development"),
    ("Strength", "End-to-End Scalable Architectures & Low-Latency AI"),
    None,
    ("Languages", "Python, C++, C, JavaScript, TypeScript, SQL"),
    ("AI / ML", "PyTorch, TensorFlow, OpenCV, Scikit-Learn"),
    ("Backend", "FastAPI, Django, Express, Node.js, REST APIs"),
    ("Frontend", "React, Next.js, TypeScript, Tailwind CSS"),
    ("Engines", "Unreal Engine, Embedded C++, Audio DSP"),
    ("Infra", "Docker, PostgreSQL, MongoDB, Supabase, Git"),
    None,
    ("Now", ["developing intelligent web applications & real-time models",
             "optimizing high-performance C++ & Unreal Engine pipelines",
             "engineering interactive full-stack user experiences"]),
    ("Next", ["quantized on-device neural acceleration",
              "spatial computing & immersive simulation engines",
              "scalable distributed cloud microservices"]),
]

W = 660
H = round(W * 875 / 840 * 370 / 490)  # -> 519
PAD = 22
TITLEBAR_H = 30
FONT = 13.5
LINE_H = 19.5
KEY_W = 11 * FONT * 0.62

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#c9d1d9"
ACCENT = "#22d3ee"
KEY = "#2dd4bf"
GREEN = "#39d353"
NEO = ["#21262d", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]

LINE_T = 0.08
LINE_DUR = 0.35

css = f"""
@keyframes in {{ 0% {{ opacity: 0; transform: translateX(-8px); }}
                 100% {{ opacity: 1; transform: translateX(0); }} }}
.l {{ opacity: 0; animation: in {LINE_DUR}s ease-out both; }}
@keyframes blink {{ 0%, 50% {{ opacity: 1; }} 51%, 100% {{ opacity: 0; }} }}
.cur {{ animation: blink 1s step-end infinite; }}
@media (prefers-reduced-motion: reduce) {{ .l {{ opacity: 1; animation: none; }} }}
""".strip()

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
]
if not STATIC:
    parts.append(f"<style>{css}</style>")
parts += [
    '<defs><linearGradient id="cbg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
    '</linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#cbg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">{USER}@{HOST}: ~$ neofetch</text>')

n = 0
y = TITLEBAR_H + 28


def line(inner, x=PAD):
    global n, y
    style = "" if STATIC else f' class="l" style="animation-delay:{0.25 + n*LINE_T:.2f}s"'
    parts.append(f'<g{style}><text x="{x:.1f}" y="{y:.1f}" font-size="{FONT}" '
                 f'xml:space="preserve">{inner}</text></g>')
    n += 1
    y += LINE_H


header = f"{USER}@{HOST}"
line(f'<tspan fill="{ACCENT}" font-weight="700">{USER}</tspan><tspan fill="{TEXT}">@</tspan>'
     f'<tspan fill="{ACCENT}" font-weight="700">{HOST}</tspan>')
line(f'<tspan fill="{MUTED}">{"-" * len(header)}</tspan>')

for row in ROWS:
    if row is None:
        y += LINE_H * 0.45
        continue
    key, val = row
    vals = val if isinstance(val, list) else [val]
    for i, v in enumerate(vals):
        k = f'<tspan fill="{KEY}" font-weight="700">{html.escape(key)}</tspan><tspan fill="{MUTED}">:</tspan>' if i == 0 else ""
        bullet = f'<tspan fill="{GREEN}">> </tspan>' if isinstance(val, list) else ""
        line(f'{k}<tspan x="{PAD + KEY_W:.1f}" fill="{TEXT}">{bullet}{html.escape(v)}</tspan>')

# neofetch color blocks + blinking cursor prompt
y += LINE_H * 0.2
style = "" if STATIC else f' class="l" style="animation-delay:{0.25 + n*LINE_T:.2f}s"'
parts.append(f"<g{style}>")
for i, c in enumerate(NEO):
    parts.append(f'<rect x="{PAD + i*26}" y="{y - 13:.1f}" width="24" height="14" rx="2" fill="{c}"/>')
parts.append("</g>")
n += 1

py = H - PAD + 2
prompt = f"{USER}@{HOST}:~$ "
style = "" if STATIC else f' class="l" style="animation-delay:{0.25 + n*LINE_T:.2f}s"'
parts.append(f'<g{style}><text x="{PAD}" y="{py}" font-size="13" fill="{MUTED}" xml:space="preserve">{prompt}</text>'
             f'<rect class="cur" x="{PAD + len(prompt)*13*0.6:.1f}" y="{py-11}" width="8" height="14" fill="{TEXT}"/></g>')

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {OUT} ({len(svg)} bytes; {W}x{H})")
