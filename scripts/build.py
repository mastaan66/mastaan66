#!/usr/bin/env python3
"""Draw the profile README's handwritten header and sketch into assets/.

Shapes use a small port of rough.js so they look drawn by hand. Words are in
Caveat, with JetBrains Mono for the plain lines. Both fonts are OFL, subset and
embedded, so the SVGs render the same everywhere. Each image sits on its own
white card, so it reads the same in GitHub's light and dark themes.
Run: python3 scripts/build.py
"""
import base64
import html
import io
import math
import random
from collections import defaultdict
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
OUT = ROOT / "assets"

# a simple light theme: dark ink on paper
T = dict(paper="#FFFFFF", edge="#E4E4E7", ink="#1F2328", muted="#59636E", warm="#D97706", cool="#0F766E")
# defaults the rough helpers fall back to
WHITE = PINK = YELLOW = GREEN = "#888888"

FACES = {
    ("mono", 400): "JetBrainsMono-400.ttf",
    ("hand", 700): "Caveat-700.ttf",
}
_font_cache = {}


def font(fam, wt):
    key = (fam, wt)
    if key not in _font_cache:
        tt = TTFont(FONTS / FACES[key])
        _font_cache[key] = (tt, tt.getBestCmap(), tt["hmtx"].metrics, tt["head"].unitsPerEm)
    return _font_cache[key]


def text_width(s, fam, wt, size, ls=0.0):
    tt, cmap, hmtx, upm = font(fam, wt)
    w = 0
    for ch in s:
        g = cmap.get(ord(ch)) or cmap.get(ord("?"))
        w += hmtx[g][0]
    return w * size / upm + ls * max(len(s) - 1, 0)


def woff2_b64(fam, wt, chars):
    cmap = font(fam, wt)[1]
    missing = sorted(c for c in chars if ord(c) not in cmap)
    if missing:
        print(f"  warning: {fam}{wt} lacks {missing}")
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt"]
    opts.name_IDs = []
    opts.notdef_outline = True
    tt = TTFont(FONTS / FACES[(fam, wt)])
    sub = subset.Subsetter(opts)
    sub.populate(text="".join(sorted(chars)) + " ")
    sub.subset(tt)
    buf = io.BytesIO()
    tt.flavor = "woff2"
    tt.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def esc(s):
    return html.escape(s, quote=True)


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.defs, self.body = [], []
        self.used = defaultdict(set)
        self._id = 0

    def uid(self, p="g"):
        self._id += 1
        return f"{p}{self._id}"

    def add(self, s):
        self.body.append(s)

    def text(self, x, y, s, fam="mono", wt=400, size=16, fill=WHITE, anchor="start",
             ls=0.0, opacity=1.0, extra=""):
        self.used[(fam, wt)].update(s)
        a = "" if anchor == "start" else f' text-anchor="{anchor}"'
        o = "" if opacity == 1 else f' fill-opacity="{opacity}"'
        l = "" if not ls else f' letter-spacing="{ls}"'
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" class="{fam}{wt}" font-size="{size}" '
                 f'fill="{fill}"{o}{a}{l} xml:space="preserve" {extra}>{esc(s)}</text>')

    def render(self):
        faces = []
        for (fam, wt), chars in sorted(self.used.items()):
            faces.append(
                f"@font-face{{font-family:'{fam}{wt}';"
                f"src:url(data:font/woff2;base64,{woff2_b64(fam, wt, chars)}) format('woff2');}}"
                f".{fam}{wt}{{font-family:'{fam}{wt}',"
                + ("'JetBrains Mono',monospace" if fam == "mono" else
                   "'Caveat',cursive" if fam == "hand" else
                   "sans-serif")
                + "}")
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{esc(self.title)}">'
                f"<title>{esc(self.title)}</title>"
                f"<style>{''.join(faces)}</style>"
                f"<defs>{''.join(self.defs)}</defs>{''.join(self.body)}</svg>")

    def save(self, name):
        OUT.mkdir(exist_ok=True)
        data = self.render()
        (OUT / name).write_text(data)
        print(f"  {name:28s} {len(data) / 1024:7.1f} KB")


# --------------------------------------------------------------------------
# rough: a compact port of the rough.js line/ellipse/hachure algorithms
# --------------------------------------------------------------------------
class Rough:
    def __init__(self, svg, seed=1, roughness=1.1, bowing=1.2):
        self.svg = svg
        self.rng = random.Random(seed)
        self.roughness = roughness
        self.bowing = bowing

    def _o(self, r):
        return self.rng.uniform(-r, r) * self.roughness

    def _line_seg(self, x1, y1, x2, y2, move=True, overlay=False):
        len_sq = (x1 - x2) ** 2 + (y1 - y2) ** 2
        length = math.sqrt(len_sq)
        gain = 1 if length < 200 else (0.4 if length > 500 else -0.0016668 * length + 1.233334)
        offset = 2.0
        if offset * offset * 100 > len_sq:
            offset = length / 10
        half = offset / 2
        diverge = 0.2 + self.rng.random() * 0.2
        mdx = self.bowing * 1.0 * (y2 - y1) / 200
        mdy = self.bowing * 1.0 * (x1 - x2) / 200
        mdx, mdy = self._o(mdx) * gain, self._o(mdy) * gain
        o = half if overlay else offset
        d = ""
        if move:
            d += f"M{x1 + self._o(o) * gain:.1f} {y1 + self._o(o) * gain:.1f}"
        d += (f"C{mdx + x1 + (x2 - x1) * diverge + self._o(o) * gain:.1f} "
              f"{mdy + y1 + (y2 - y1) * diverge + self._o(o) * gain:.1f} "
              f"{mdx + x1 + 2 * (x2 - x1) * diverge + self._o(o) * gain:.1f} "
              f"{mdy + y1 + 2 * (y2 - y1) * diverge + self._o(o) * gain:.1f} "
              f"{x2 + self._o(o) * gain:.1f} {y2 + self._o(o) * gain:.1f}")
        return d

    def _stroke(self, d, color, width, extra=""):
        self.svg.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
                     f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')

    def line(self, x1, y1, x2, y2, color=WHITE, width=2.2, double=True):
        d = self._line_seg(x1, y1, x2, y2)
        if double:
            d += self._line_seg(x1, y1, x2, y2, overlay=True)
        self._stroke(d, color, width)

    def poly(self, pts, color=WHITE, width=2.2, closed=True):
        pts = list(pts) + ([pts[0]] if closed else [])
        d = ""
        for a, b in zip(pts, pts[1:]):
            d += self._line_seg(*a, *b) + self._line_seg(*a, *b, overlay=True)
        self._stroke(d, color, width)

    def _hachure(self, clip_shape, box, color, gap=9, angle=-41, width=1.6):
        cid = self.svg.uid("clip")
        self.svg.defs.append(f'<clipPath id="{cid}">{clip_shape}</clipPath>')
        x, y, w, h = box
        cx, cy = x + w / 2, y + h / 2
        r = math.hypot(w, h) / 2 + gap
        a = math.radians(angle)
        dx, dy = math.cos(a), math.sin(a)
        nx, ny = -dy, dx
        d = ""
        k = -r
        while k <= r:
            px, py = cx + nx * k, cy + ny * k
            d += self._line_seg(px - dx * r, py - dy * r, px + dx * r, py + dy * r)
            k += gap
        self._stroke(d, color, width, f'clip-path="url(#{cid})" stroke-opacity="0.85"')

    def rect(self, x, y, w, h, color=WHITE, width=2.2, fill=None, gap=9, solid=None):
        if solid:
            self.svg.add(f'<rect x="{x + 3}" y="{y + 3}" width="{w - 4}" height="{h - 4}" '
                         f'rx="4" fill="{solid}"/>')
        if fill:
            self._hachure(f'<rect x="{x + 2}" y="{y + 2}" width="{w - 4}" height="{h - 4}"/>',
                          (x, y, w, h), fill, gap)
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], color, width)

    def _ellipse_path(self, cx, cy, w, h, overlap):
        rx, ry = w / 2, h / 2
        steps = max(10, int(math.sqrt(2 * math.pi * math.sqrt((rx * rx + ry * ry) / 2)) * 1.4))
        inc = 2 * math.pi / steps
        start = self.rng.random() * 2 * math.pi
        rough = 1 + self.roughness * 0.1
        jitter = min(0.05, 7 / max(rx, ry))  # big shapes wobble less, like rough.js
        pts = []
        t = start - inc
        while t < start + 2 * math.pi + overlap:
            rr = 1 + self._o(jitter) * rough
            pts.append((cx + rx * rr * math.cos(t) + self._o(0.6),
                        cy + ry * rr * math.sin(t) + self._o(0.6)))
            t += inc
        return catmull(pts)

    def ellipse(self, cx, cy, w, h, color=WHITE, width=2.2, fill=None, gap=9, solid=None):
        if solid:
            self.svg.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{w / 2 - 3}" ry="{h / 2 - 3}" fill="{solid}"/>')
        if fill:
            self._hachure(f'<ellipse cx="{cx}" cy="{cy}" rx="{w / 2 - 2}" ry="{h / 2 - 2}"/>',
                          (cx - w / 2, cy - h / 2, w, h), fill, gap)
        d = self._ellipse_path(cx, cy, w, h, 0.4) + self._ellipse_path(cx, cy, w, h, 0.2)
        self._stroke(d, color, width)

    def curve(self, pts, color=WHITE, width=2.2, double=True):
        d = ""
        for _ in range(2 if double else 1):
            d += catmull([(x + self._o(1.5), y + self._o(1.5)) for x, y in pts])
        self._stroke(d, color, width)

    def arrow(self, pts, color=WHITE, width=2.2, head=13):
        """Hand-drawn arrow along a smooth path through pts (>=2 points)."""
        if len(pts) == 2:
            (x1, y1), (x2, y2) = pts
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            pts = [(x1, y1), (mx + self._o(4), my + self._o(4)), (x2, y2)]
        self.curve(pts, color, width)
        (ax, ay), (bx, by) = pts[-2], pts[-1]
        ang = math.atan2(by - ay, bx - ax)
        for s in (-1, 1):
            a = ang + math.pi + s * 0.45
            self.line(bx, by, bx + head * math.cos(a), by + head * math.sin(a), color, width)

    def underline(self, x, y, w, color=PINK, width=3):
        pts = [(x + i * w / 6, y + (3 if i % 2 else -2) + self._o(1.5)) for i in range(7)]
        self.curve(pts, color, width)

    def star(self, cx, cy, r, color=YELLOW, width=2):
        pts = []
        for i in range(10):
            rr = r if i % 2 == 0 else r * 0.45
            a = -math.pi / 2 + i * math.pi / 5
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        self.poly(pts, color, width)

def catmull(pts):
    if len(pts) < 3:
        (x1, y1), (x2, y2) = pts
        return f"M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}"
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    p = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d



def hand(s, x, y, t, size, col, anchor="start", rot=0):
    extra = f'transform="rotate({rot} {x} {y})"' if rot else ""
    s.text(x, y, t, "hand", 700, size, col, anchor, extra=extra)


def paper(s):
    s.add(f'<rect x="1" y="1" width="{s.w - 2}" height="{s.h - 2}" rx="16" fill="{T["paper"]}" stroke="{T["edge"]}"/>')


def header():
    s = Svg(1280, 300, "hi, I'm Mastan. Backend and systems engineer.")
    paper(s)
    r = Rough(s, seed=7)
    # doodled mark: three connected nodes, a tiny distributed system
    nodes = [(84, 190, T["cool"]), (124, 110, T["warm"]), (164, 190, T["ink"])]
    for (ax, ay, _), (bx, by, _) in zip(nodes, nodes[1:] + nodes[:1]):
        r.line(ax, ay, bx, by, T["muted"], 2)
    for x, y, col in nodes:
        r.ellipse(x, y, 30, 30, col, 2.4, fill=col, gap=5)

    hand(s, 214, 160, "hi, I'm Mastan", 104, T["ink"])
    r.underline(222, 184, text_width("hi, I'm Mastan", "hand", 700, 104) - 16, T["warm"], 3.4)
    s.text(218, 234, "backend & systems engineer", "mono", 400, 22, T["muted"])
    s.text(218, 268, "distributed systems · payments · AI agents", "mono", 400, 22, T["muted"])

    hand(s, 1060, 128, "currently building", 34, T["cool"], "middle", rot=-5)
    hand(s, 1064, 166, "@ Lumenar", 34, T["cool"], "middle", rot=-5)
    r.star(1180, 70, 12, T["warm"], 2)
    s.save("header.svg")


def foreman_sketch():
    s = Svg(1280, 500, "Sketch: how Foreman runs a team of AI coding agents. A director writes tickets "
                       "for a lead, who hands work to coder, tester, drone and librarian agents under a budget gate.")
    paper(s)
    r = Rough(s, seed=404)
    ink, muted, warm, cool = T["ink"], T["muted"], T["warm"], T["cool"]

    hand(s, 40, 56, "how foreman runs a team of agents", 40, ink)
    r.underline(44, 72, text_width("how foreman runs a team of agents", "hand", 700, 40) - 8, warm, 3)

    r.rect(545, 100, 190, 64, ink, fill=warm, gap=11)
    hand(s, 640, 142, "director", 32, ink, "middle")
    r.poly([(612, 92), (618, 70), (630, 84), (640, 66), (650, 84), (662, 70), (668, 92)], warm, 2)
    r.arrow([(640, 168), (640, 222)], ink, 2)
    hand(s, 656, 204, "tickets", 24, muted)

    r.rect(545, 228, 190, 64, ink, fill=warm, gap=11)
    hand(s, 640, 270, "lead", 32, ink, "middle")
    hand(s, 750, 266, "plans · reviews · gates", 24, muted)

    for i, (name, tier) in enumerate([("coder", "standard"), ("tester", "standard"),
                                      ("drone", "economy"), ("librarian", "economy")]):
        cx = 340 + i * 200
        r.arrow([(640, 296), ((640 + cx) / 2 + 12, 340), (cx, 374)], ink, 1.8, head=10)
        r.rect(cx - 75, 380, 150, 60, ink, fill=cool, gap=12)
        hand(s, cx, 418, name, 30, ink, "middle")
        hand(s, cx, 470, tier, 22, muted, "middle")

    r.rect(80, 190, 210, 84, muted, 1.8)
    hand(s, 185, 226, "$ budget gate", 28, cool, "middle")
    hand(s, 185, 258, "hard stop, no surprises", 22, muted, "middle")
    hand(s, 1110, 150, "all via opencode", 28, cool, "middle", rot=-6)
    s.save("sketch-foreman.svg")


def main():
    print("drawing assets/")
    for old in OUT.glob("*"):
        old.unlink()
    header()
    foreman_sketch()


if __name__ == "__main__":
    main()
