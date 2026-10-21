#!/usr/bin/env python3
"""
Author the hero banner SVG: handle, name, a typewriter tagline that cycles
through phrases, skill pills, and a floating isometric code cube.

    python scripts/make_hero_banner.py           # writes hero-banner.svg
    STATIC=1 python scripts/make_hero_banner.py  # frozen frame for previews
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "hero-banner.svg")
STATIC = bool(os.environ.get("STATIC"))

HANDLE = "@niralichandra"
NAME = "Nirali Chandra"
PHRASES = [
    "building intelligent systems",
    "shipping full-stack apps",
    "crafting worlds in Unreal",
]
PILLS = ["Python", "C++", "Unreal Engine", "PyTorch", "React"]

W = 860
H = 350
TITLEBAR_H = 30
SHIFT = 18  # content offset below the title bar
PROMPT_USER = "nirali@github"

# same monochrome terminal palette as the portrait and info card
BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
DOT = "#1c2128"
MUTED = "#7d8590"
TEXT = "#c9d1d9"
HEAD = "#e6edf3"
ACCENT = TEXT
PILL_BG = "#161b22"
PILL_EDGE = FRAME
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# typewriter timing (seconds)
TYPE_T = 0.075
ERASE_T = 0.035
HOLD_T = 2.4
GAP_T = 0.5

TAG_X = 58
TAG_Y = 196
TAG_FONT = 20
CHAR_W = TAG_FONT * 0.6
PROMPT = "> "

# cube geometry
CX, CY, S = 690, 92, 62
DX, DY = S * 0.866, S * 0.5


def esc(s):
    return html.escape(s, quote=True)


def typewriter():
    """Per-character opacity keyframes plus a stepped cursor, one shared cycle."""
    spans = []
    for p in PHRASES:
        n = len(p)
        type_end = n * TYPE_T
        erase_start = type_end + HOLD_T
        spans.append((p, type_end, erase_start, erase_start + n * ERASE_T + GAP_T))
    cycle = sum(s[3] for s in spans)
    pct = lambda t: f"{t / cycle * 100:.3f}%"

    css, nodes = [], []
    base_x = TAG_X + len(PROMPT) * CHAR_W
    cursor_stops = []
    t0 = 0.0
    for pi, (p, type_end, erase_start, dur) in enumerate(spans):
        n = len(p)
        for j, ch in enumerate(p):
            on = t0 + (j + 1) * TYPE_T
            off = t0 + erase_start + (n - j) * ERASE_T
            name = f"c{pi}_{j}"
            css.append(
                f"@keyframes {name}{{0%,{pct(on - 0.001)}{{opacity:0}}"
                f"{pct(on)},{pct(off - 0.001)}{{opacity:1}}{pct(off)},100%{{opacity:0}}}}"
            )
            if ch != " ":
                x = base_x + j * CHAR_W
                style = "" if STATIC else f' style="animation:{name} {cycle:.3f}s infinite"'
                opacity = "1" if (STATIC and pi == 0) else "0"
                nodes.append(f'<text x="{x:.1f}" y="{TAG_Y}" opacity="{opacity}"{style}>{esc(ch)}</text>')
        for j in range(n + 1):
            cursor_stops.append((t0 + j * TYPE_T, j))
        for j in range(n, -1, -1):
            cursor_stops.append((t0 + erase_start + (n - j) * ERASE_T, j))
        t0 += dur

    frames = "".join(f"{pct(t)}{{transform:translateX({j * CHAR_W:.1f}px)}}" for t, j in cursor_stops)
    css.append(f"@keyframes cur{{{frames}}}")
    css.append(f".cur{{animation:cur {cycle:.3f}s step-end infinite,blink 1s step-end infinite}}")
    if STATIC:
        nodes.append(
            f'<rect x="{base_x + len(PHRASES[0]) * CHAR_W:.1f}" y="{TAG_Y + 1}" width="11" height="3" fill="{ACCENT}"/>'
        )
    else:
        nodes.append(f'<rect class="cur" x="{base_x:.1f}" y="{TAG_Y + 1}" width="11" height="3" fill="{ACCENT}"/>')
    return css, nodes


def cube():
    top = [(CX, CY), (CX + DX, CY + DY), (CX, CY + 2 * DY), (CX - DX, CY + DY)]
    left = [(CX - DX, CY + DY), (CX, CY + 2 * DY), (CX, CY + 2 * DY + S), (CX - DX, CY + DY + S)]
    right = [(CX, CY + 2 * DY), (CX + DX, CY + DY), (CX + DX, CY + DY + S), (CX, CY + 2 * DY + S)]
    pts = lambda ps: " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)
    lx, ly = left[0]
    rx, ry = right[0]
    return f"""
  <g class="float">
    <polygon points="{pts(top)}" fill="#2d333b" stroke="{MUTED}" stroke-width="1.2" stroke-linejoin="round"/>
    <polygon points="{pts(left)}" fill="#1c2128" stroke="{MUTED}" stroke-width="1.2" stroke-linejoin="round"/>
    <polygon points="{pts(right)}" fill="#161b22" stroke="{MUTED}" stroke-width="1.2" stroke-linejoin="round"/>
    <g transform="matrix(0.866 0.5 0 1 {lx:.1f} {ly:.1f})" font-family="{MONO}" font-weight="700" font-size="21" fill="{TEXT}">
      <text x="11" y="40">&lt;/&gt;</text>
    </g>
    <g transform="matrix(0.866 -0.5 0 1 {rx:.1f} {ry:.1f})" font-family="{MONO}" font-weight="700" font-size="24" fill="{TEXT}">
      <text x="12" y="40">{{ }}</text>
    </g>
    <circle cx="{CX - 6}" cy="{CY + 22}" r="4" fill="{TEXT}" class="pulse"/>
  </g>"""


def pills():
    out, x, y = [], 58, 236
    for i, label in enumerate(PILLS):
        w = round(len(label) * 8.3 + 34)
        style = "" if STATIC else f' style="animation:up .6s ease-out {1.0 + i * 0.12:.2f}s both"'
        out.append(
            f'<g{style}><rect x="{x}" y="{y}" width="{w}" height="36" rx="18" fill="{PILL_BG}" '
            f'stroke="{PILL_EDGE}" stroke-width="1.2"/>'
            f'<text x="{x + w / 2}" y="{y + 23.5}" text-anchor="middle">{esc(label)}</text></g>'
        )
        x += w + 12
    return out


def build():
    tw_css, tw_nodes = typewriter()
    css = "\n".join([
        "@keyframes up{0%{opacity:0;transform:translateY(10px)}100%{opacity:1;transform:none}}",
        "@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}",
        "@keyframes shadow{0%,100%{transform:scale(1);opacity:.55}50%{transform:scale(.86);opacity:.35}}",
        "@keyframes blink{0%,50%{opacity:1}51%,100%{opacity:0}}",
        "@keyframes dash{to{stroke-dashoffset:-120}}",
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}",
        ".float{animation:float 6s ease-in-out infinite}",
        f".shadow{{animation:shadow 6s ease-in-out infinite;transform-origin:{CX}px 272px}}",
        ".orbit{animation:dash 14s linear infinite}",
        ".pulse{animation:pulse 2.4s ease-in-out infinite}",
        ".h{animation:up .7s ease-out .1s both}",
        ".n{animation:up .7s ease-out .3s both}",
        *tw_css,
    ])

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="{esc(NAME)}: {esc(", ".join(PHRASES))}">',
        f"<title>{esc(NAME)}</title>",
    ]
    if not STATIC:
        parts.append(f"<style>{css}</style>")
    parts.append(f"""
  <defs>
    <linearGradient id="gBg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>
    </linearGradient>
    <pattern id="pDots" width="22" height="22" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="{DOT}"/>
    </pattern>
  </defs>

  <rect width="{W}" height="{H}" rx="12" fill="url(#gBg)"/>
  <rect y="{TITLEBAR_H}" width="{W}" height="{H - TITLEBAR_H - 12}" fill="url(#pDots)"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{FRAME}"/>
  <line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>
  {''.join(f'<circle cx="{20 + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{c}"/>' for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]))}
  <text x="{W / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{MUTED}" font-family="{MONO}" font-size="12" text-anchor="middle">{PROMPT_USER}: ~$ ./hello.sh</text>

  <g transform="translate(0 {SHIFT})">
  <ellipse class="shadow" cx="{CX}" cy="272" rx="58" ry="8" fill="#010409"/>
  <ellipse class="orbit" cx="{CX}" cy="{CY + 70}" rx="140" ry="40" transform="rotate(-12 {CX} {CY + 70})"
           fill="none" stroke="{MUTED}" stroke-opacity=".45" stroke-width="1" stroke-dasharray="4 7"/>
  {cube()}

  <text class="h" x="58" y="78" font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="4.5" fill="{MUTED}">{esc(HANDLE.upper())}</text>
  <text class="n" x="56" y="146" font-family="{SANS}" font-size="60" font-weight="800" fill="{HEAD}" letter-spacing="-.5">{esc(NAME)}</text>
  <g font-family="{MONO}" font-size="{TAG_FONT}" fill="{ACCENT}">
    <text x="{TAG_X}" y="{TAG_Y}">{esc(PROMPT.strip())}</text>
    {''.join(tw_nodes)}
  </g>
  <g font-family="{SANS}" font-size="14" font-weight="700" fill="{HEAD}">
    {''.join(pills())}
  </g>
  </g>
</svg>
""")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = build()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {os.path.abspath(OUT)} {len(svg.encode())} bytes; {W} x {H}")
