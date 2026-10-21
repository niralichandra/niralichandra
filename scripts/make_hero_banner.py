#!/usr/bin/env python3
"""
Author the hero banner SVG: text only, no card. The name is drawn in pixel
blocks that "generate" out of flickering noise, resolving top to bottom like an
image model rendering, followed by a typewriter tagline that cycles phrases.

    python scripts/make_hero_banner.py           # writes hero-banner.svg
    STATIC=1 python scripts/make_hero_banner.py  # frozen frame for previews
"""
import html
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
STATIC = bool(os.environ.get("STATIC"))

NAME = "NIRALI CHANDRA"
PHRASES = [
    "building intelligent systems",
    "shipping full-stack apps",
    "crafting worlds in Unreal",
]

W = 860
H = 170

# white pixels, grey noise, light-grey tagline
INK = "#ffffff"
DIM = "#484f58"
TEXT = "#c9d1d9"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# pixel grid
CELL = 10
PIX = 8
NAME_Y = 16
NOISE_P = 0.35

# generation timing (seconds)
RES_START = 0.5   # first row locks in
RES_ROW = 0.17    # extra delay per row
RES_JITTER = 0.45
LIT_T = 1.1       # each lit pixel: noise -> dim -> solid
NOISE_T = 1.4

# typewriter timing (seconds)
TYPE_T = 0.075
ERASE_T = 0.035
HOLD_T = 2.4
GAP_T = 0.5
TYPE_START = 2.2  # let the name finish generating first

TAG_Y = 138
TAG_FONT = 20
CHAR_W = TAG_FONT * 0.6
PROMPT = "> "

# 5x7 bitmap glyphs ("#" = lit)
GLYPHS = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "N": ["#...#", "##..#", "#.#.#", "#.#.#", "#.#.#", "#..##", "#...#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    " ": ["..."] * 7,
}


def esc(s):
    return html.escape(s, quote=True)


def pixel_name():
    """Lit pixels resolve top-down with jitter; noise pixels flicker then clear."""
    cols = sum(len(GLYPHS[ch][0]) + 1 for ch in NAME) - 1
    x0 = (W - cols * CELL) / 2
    rng = random.Random(7)
    lit, noise = [], []
    cx = 0
    for ch in NAME:
        g = GLYPHS[ch]
        gw = len(g[0])
        for r in range(7):
            for c in range(gw + 1):
                on = c < gw and g[r][c] == "#"
                x = x0 + (cx + c) * CELL
                y = NAME_Y + r * CELL
                if on:
                    lit.append((x, y, r))
                elif cx + c < cols and rng.random() < NOISE_P:
                    noise.append((x, y, r))
        cx += gw + 1

    out = []
    for x, y, r in lit:
        if STATIC:
            out.append(f'<rect x="{x:.0f}" y="{y}" width="{PIX}" height="{PIX}" class="ink"/>')
            continue
        done = RES_START + r * RES_ROW + rng.random() * RES_JITTER
        out.append(
            f'<rect x="{x:.0f}" y="{y}" width="{PIX}" height="{PIX}" class="lit" '
            f'style="animation-delay:{max(done - LIT_T, 0):.2f}s"/>'
        )
    if not STATIC:
        for x, y, r in noise:
            start = rng.random() * (RES_START + r * RES_ROW)
            out.append(
                f'<rect x="{x:.0f}" y="{y}" width="{PIX}" height="{PIX}" class="nz" '
                f'style="animation-delay:{start:.2f}s"/>'
            )
    return out, x0, cols * CELL


def typewriter(x_start):
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
    base_x = x_start + len(PROMPT) * CHAR_W
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
                style = "" if STATIC else f' style="animation:{name} {cycle:.3f}s {TYPE_START}s infinite both"'
                opacity = "1" if (STATIC and pi == 0) else "0"
                nodes.append(f'<text x="{x:.1f}" y="{TAG_Y}" opacity="{opacity}"{style}>{esc(ch)}</text>')
        for j in range(n + 1):
            cursor_stops.append((t0 + j * TYPE_T, j))
        for j in range(n, -1, -1):
            cursor_stops.append((t0 + erase_start + (n - j) * ERASE_T, j))
        t0 += dur

    frames = "".join(f"{pct(t)}{{transform:translateX({j * CHAR_W:.1f}px)}}" for t, j in cursor_stops)
    css.append(f"@keyframes cur{{{frames}}}")
    css.append(f".cur{{animation:cur {cycle:.3f}s step-end {TYPE_START}s infinite,blink 1s step-end infinite}}")
    cur_x = base_x + (len(PHRASES[0]) * CHAR_W if STATIC else 0)
    nodes.append(f'<rect class="cur tx" x="{cur_x:.1f}" y="{TAG_Y + 1}" width="11" height="3"/>')
    return css, nodes


def build():
    pixels, name_x, _ = pixel_name()
    longest = max(len(p) for p in PHRASES) + len(PROMPT)
    tag_x = (W - longest * CHAR_W) / 2
    tw_css, tw_nodes = typewriter(tag_x)

    css = "\n".join([
        f"svg{{--ink:{INK};--dim:{DIM};--text:{TEXT}}}",
        ".ink{fill:var(--ink)}",
        ".tx{fill:var(--text)}",
        # lit pixel: flickers as noise, settles dim, then snaps solid
        "@keyframes lit{0%{opacity:0;fill:var(--dim)}15%{opacity:.6}30%{opacity:.15}"
        "50%{opacity:.7;fill:var(--dim)}75%{opacity:.4}100%{opacity:1;fill:var(--ink)}}",
        "@keyframes nz{0%{opacity:0}20%{opacity:.55}40%{opacity:.1}60%{opacity:.45}80%{opacity:.15}100%{opacity:0}}",
        "@keyframes blink{0%,50%{opacity:1}51%,100%{opacity:0}}",
        f".lit{{fill:var(--ink);animation:lit {LIT_T}s steps(6,end) both}}",
        f".nz{{fill:var(--dim);opacity:0;animation:nz {NOISE_T}s steps(5,end) both}}",
        *tw_css,
    ])

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="Nirali Chandra: {esc(", ".join(PHRASES))}">',
        "<title>Nirali Chandra</title>",
        f"<style>{css if not STATIC else css.split('@keyframes lit')[0]}</style>",
        f'<g shape-rendering="crispEdges">{"".join(pixels)}</g>',
        f'<g class="tx" font-family="{MONO}" font-size="{TAG_FONT}">',
        f'<text x="{tag_x:.1f}" y="{TAG_Y}">{esc(PROMPT.strip())}</text>',
        *tw_nodes,
        "</g>",
        "</svg>",
    ]
    return "\n".join(parts)


if __name__ == "__main__":
    out = os.path.join(ROOT, "hero-banner.svg")
    svg = build()
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {os.path.abspath(out)} {len(svg.encode())} bytes; {W} x {H}")
