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
H = 330
INSET = 6

BG_A = "#0b2a2c"
BG_B = "#0a1a24"
FRAME = "#1f4d4f"
DOT = "#2a5d5e"
HEAD = "#ccfbf1"
ACCENT = "#2dd4bf"
SKY = "#7dd3fc"
PILL_BG = "#0f3b3c"
PILL_EDGE = "#2dd4bf"
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
    <polygon points="{pts(top)}" fill="url(#gTop)" stroke="{HEAD}" stroke-width="1.4" stroke-linejoin="round"/>
    <polygon points="{pts(left)}" fill="url(#gLeft)" stroke="{HEAD}" stroke-width="1.4" stroke-linejoin="round"/>
    <polygon points="{pts(right)}" fill="url(#gRight)" stroke="{HEAD}" stroke-width="1.4" stroke-linejoin="round"/>
    <g transform="matrix(0.866 0.5 0 1 {lx:.1f} {ly:.1f})" font-family="{MONO}" font-weight="700" font-size="21" fill="#06302f">
      <text x="11" y="40">&lt;/&gt;</text>
    </g>
    <g transform="matrix(0.866 -0.5 0 1 {rx:.1f} {ry:.1f})" font-family="{MONO}" font-weight="700" font-size="24" fill="{HEAD}">
      <text x="12" y="40">{{ }}</text>
    </g>
    <circle cx="{CX - 6}" cy="{CY + 22}" r="5" fill="{SKY}" class="pulse"/>
    <circle cx="{CX + 18}" cy="{CY + 2 * DY + S - 20}" r="5" fill="{HEAD}"/>
  </g>"""


def pills():
    out, x, y = [], 58, 236
    for i, label in enumerate(PILLS):
        w = round(len(label) * 8.3 + 34)
        style = "" if STATIC else f' style="animation:up .6s ease-out {1.0 + i * 0.12:.2f}s both"'
        out.append(
            f'<g{style}><rect x="{x}" y="{y}" width="{w}" height="36" rx="18" fill="{PILL_BG}" '
            f'stroke="{PILL_EDGE}" stroke-opacity=".75" stroke-width="1.2"/>'
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
        "@keyframes slide{0%,100%{transform:translateX(0)}50%{transform:translateX(120px)}}",
        "@keyframes tw{0%,100%{opacity:.15}50%{opacity:.9}}",
        ".float{animation:float 6s ease-in-out infinite}",
        f".shadow{{animation:shadow 6s ease-in-out infinite;transform-origin:{CX}px 272px}}",
        ".orbit{animation:dash 14s linear infinite}",
        ".pulse{animation:pulse 2.4s ease-in-out infinite}",
        ".slide{animation:slide 9s ease-in-out infinite}",
        ".tw{animation:tw 3s ease-in-out infinite}",
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
    <linearGradient id="gBg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG_A}"/><stop offset="1" stop-color="{BG_B}"/>
    </linearGradient>
    <radialGradient id="gGlowL" cx="0.22" cy="0.25" r="0.45">
      <stop offset="0" stop-color="{ACCENT}" stop-opacity=".22"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="gGlowR" cx="0.8" cy="0.5" r="0.35">
      <stop offset="0" stop-color="{ACCENT}" stop-opacity=".2"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="gTop" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#e6fffb"/><stop offset="1" stop-color="#99f6e4"/>
    </linearGradient>
    <linearGradient id="gLeft" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#5eead4"/><stop offset="1" stop-color="#14b8a6"/>
    </linearGradient>
    <linearGradient id="gRight" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#14b8a6"/><stop offset="1" stop-color="#0f766e"/>
    </linearGradient>
    <pattern id="pDots" width="22" height="22" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="{DOT}"/>
    </pattern>
    <clipPath id="clip"><rect x="{INSET}" y="{INSET}" width="{W - 2 * INSET}" height="{H - 2 * INSET}" rx="22"/></clipPath>
  </defs>

  <g clip-path="url(#clip)">
    <rect width="{W}" height="{H}" fill="url(#gBg)"/>
    <rect width="{W}" height="{H}" fill="url(#pDots)" opacity=".55"/>
    <rect width="{W}" height="{H}" fill="url(#gGlowL)"/>
    <rect width="{W}" height="{H}" fill="url(#gGlowR)"/>
    <rect class="slide" x="520" y="{INSET}" width="48" height="2" fill="{ACCENT}" opacity=".8"/>
    <rect class="slide" x="300" y="{H - INSET - 2}" width="48" height="2" fill="{ACCENT}" opacity=".6" style="animation-delay:-4s"/>
    <circle class="tw" cx="452" cy="298" r="2" fill="{SKY}"/>
    <circle class="tw" cx="586" cy="300" r="1.6" fill="{HEAD}" style="animation-delay:-1.5s"/>
    <circle class="tw" cx="808" cy="58" r="1.6" fill="{HEAD}" style="animation-delay:-.7s"/>
  </g>
  <rect x="{INSET}" y="{INSET}" width="{W - 2 * INSET}" height="{H - 2 * INSET}" rx="22" fill="none" stroke="{FRAME}" stroke-width="1.2"/>

  <ellipse class="shadow" cx="{CX}" cy="272" rx="58" ry="9" fill="#04191b"/>
  <ellipse class="orbit" cx="{CX}" cy="{CY + 70}" rx="140" ry="40" transform="rotate(-12 {CX} {CY + 70})"
           fill="none" stroke="{ACCENT}" stroke-opacity=".35" stroke-width="1.2" stroke-dasharray="5 7"/>
  {cube()}

  <text class="h" x="58" y="78" font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="4.5" fill="{ACCENT}">{esc(HANDLE.upper())}</text>
  <text class="n" x="56" y="146" font-family="{SANS}" font-size="60" font-weight="800" fill="{HEAD}" letter-spacing="-.5">{esc(NAME)}</text>
  <g font-family="{MONO}" font-size="{TAG_FONT}" fill="{ACCENT}">
    <text x="{TAG_X}" y="{TAG_Y}">{esc(PROMPT.strip())}</text>
    {''.join(tw_nodes)}
  </g>
  <g font-family="{SANS}" font-size="14" font-weight="700" fill="{HEAD}">
    {''.join(pills())}
  </g>
</svg>
""")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = build()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {os.path.abspath(OUT)} {len(svg.encode())} bytes; {W} x {H}")
