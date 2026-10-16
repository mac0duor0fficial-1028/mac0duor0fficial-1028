#!/usr/bin/env python3
"""
Generates every SVG used by README.md (all text is set in Space Grotesk,
embedded as base64 so it renders anywhere, including GitHub).

  python scripts/generate.py          -> rebuild all static assets
  python scripts/generate.py stats    -> rebuild assets/stats.svg from live GitHub data
                                         (needs env GH_TOKEN and GH_USER)
"""
import base64, html, json, math, os, re, sys, urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
ICONS = os.path.join(ROOT, "scripts", "icons")
FONTS = os.path.join(ASSETS, "fonts")
USER = os.environ.get("GH_USER", "mac0duor0fficial-1028")

# ── design tokens ─────────────────────────────────────────────
BG, CARD, BORDER = "#0d1117", "#141a22", "#2a313c"
TXT, SOFT, MUTED = "#f6ede4", "#c5ccd6", "#8d97a6"
C1, C2, C3 = "#e4a672", "#ff5f6d", "#ffc371"

# ── helpers ───────────────────────────────────────────────────
_font_cache = {}
def font_css(weights):
    out = []
    for w in weights:
        if w not in _font_cache:
            p = os.path.join(FONTS, f"space-grotesk-latin-{w}-normal.woff2")
            _font_cache[w] = base64.b64encode(open(p, "rb").read()).decode()
        out.append("@font-face{font-family:'Space Grotesk';font-weight:%d;"
                   "src:url(data:font/woff2;base64,%s) format('woff2');}" % (w, _font_cache[w]))
    return "".join(out)

_icon_cache = {}
def icon(name, x, y, size, color, sw=2.0, extra=""):
    if name not in _icon_cache:
        raw = open(os.path.join(ICONS, name + ".svg")).read()
        _icon_cache[name] = re.search(r"<svg[^>]*>(.*)</svg>", raw, re.S).group(1)
    return (f'<g transform="translate({x} {y}) scale({size/24})" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extra}>{_icon_cache[name]}</g>')

def T(x, y, s, size=16, w=400, fill=TXT, anchor="start", ls=0, cls="", extra=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{fill}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}"{c} {extra}>{html.escape(s, quote=False)}</text>')

GRAD = (f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{C1}"/><stop offset=".5" stop-color="{C2}"/>'
        f'<stop offset="1" stop-color="{C3}"/></linearGradient>')

def doc(w, h, body, title, defs="", css="", weights=(400, 500, 700)):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title>'
            f'<defs>{GRAD}{defs}</defs>'
            f'<style>{font_css(weights)}text{{font-family:\'Space Grotesk\',system-ui,sans-serif}}{css}</style>'
            f'{body}</svg>')

def save(name, svg):
    os.makedirs(ASSETS, exist_ok=True)
    open(os.path.join(ASSETS, name), "w").write(svg)
    print(f"  {name:28s}{len(svg)//1024:4d} KB")

def card(x, y, w, h, r=16, fill=CARD, stroke=BORDER):
    return f'<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'

def tile(x, y, s, name, grad=True, color=BG, tint=None, sw=2.2):
    fill = "url(#g)" if grad else (tint or "rgba(255,255,255,.06)")
    stroke = "" if grad else f' stroke="{BORDER}"'
    return (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{s*.3:.0f}" fill="{fill}"{stroke}/>'
            + icon(name, x + s*.22, y + s*.22, s*.56, color, sw))

# ══════════════════════════════ HERO ══════════════════════════════
def hero():
    W, H = 900, 340
    defs = (f'<clipPath id="cl"><rect width="{W}" height="{H}" rx="26"/></clipPath>'
            '<filter id="b" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="55"/></filter>'
            '<filter id="glow"><feGaussianBlur stdDeviation="3"/></filter>'
            '<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
            '<circle cx="1.5" cy="1.5" r="1" fill="#fff" opacity=".07"/></pattern>'
            f'<linearGradient id="ng" gradientUnits="userSpaceOnUse" x1="44" y1="0" x2="344" y2="0" spreadMethod="reflect">'
            f'<stop offset="0" stop-color="{C1}"/><stop offset=".5" stop-color="{C2}"/><stop offset="1" stop-color="{C3}"/>'
            '<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="600 0" dur="9s" repeatCount="indefinite"/>'
            '</linearGradient>')
    css = (".cyc{opacity:0;animation:cyc 9s infinite}.c2{animation-delay:3s}.c3{animation-delay:6s}"
           "@keyframes cyc{0%{opacity:0;transform:translateY(8px)}6%,30%{opacity:1;transform:translateY(0)}"
           "36%,100%{opacity:0;transform:translateY(-8px)}}"
           ".flow{stroke-dasharray:6 10;animation:flow 1.2s linear infinite}@keyframes flow{to{stroke-dashoffset:-16}}"
           ".float{animation:fl 7s ease-in-out infinite}@keyframes fl{50%{transform:translateY(-12px)}}")
    b = f'<rect width="{W}" height="{H}" rx="26" fill="{BG}"/><g clip-path="url(#cl)">'
    for cx, cy, r, col, op, dx, dy, d in [(140, 40, 170, C2, .38, 70, 30, 9), (790, 330, 190, C3, .30, -60, -30, 11), (480, 190, 120, C1, .16, 40, -40, 13)]:
        b += (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}" opacity="{op}" filter="url(#b)">'
              f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" dur="{d}s" repeatCount="indefinite"/></circle>')
    b += f'<rect width="{W}" height="{H}" fill="url(#dots)"/>'
    # decorative layers icon
    b += f'<g class="float">{icon("layers", 610, 38, 230, "url(#g)", .55, "opacity=\".75\"")}</g>'
    b += f'<g class="float" style="animation-delay:-3s">{icon("database", 722, 168, 96, C3, .9, "opacity=\".5\"")}</g>'
    # data stream
    b += (f'<line x1="44" y1="304" x2="856" y2="304" stroke="#fff" stroke-opacity=".12" stroke-width="2"/>'
          f'<line class="flow" x1="44" y1="304" x2="856" y2="304" stroke="url(#g)" stroke-width="2"/>')
    for nx in (44, 247, 450, 653, 856):
        b += f'<circle cx="{nx}" cy="304" r="5" fill="{BG}" stroke="{C3}" stroke-width="2"/>'
    for i in range(3):
        b += (f'<circle r="5" fill="{C3}" filter="url(#glow)"><animateMotion dur="5s" begin="{i*1.65}s" repeatCount="indefinite" path="M44 304 H856"/></circle>'
              f'<circle r="3" fill="#fff"><animateMotion dur="5s" begin="{i*1.65}s" repeatCount="indefinite" path="M44 304 H856"/></circle>')
    b += '</g>'
    b += f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="26" fill="none" stroke="{BORDER}"/>'
    # pill
    b += (f'<rect x="44" y="40" width="334" height="36" rx="18" fill="rgba(255,255,255,.07)" stroke="rgba(255,255,255,.18)"/>'
          + icon("database", 58, 48, 20, C3, 2)
          + T(88, 63, "DATA INFRASTRUCTURE ARCHITECT", 13, 500, TXT, ls=2))
    b += T(40, 168, "Macphalen", 96, 700, "url(#ng)", ls=-3)
    b += T(44, 216, "Turning raw data chaos into trusted assets.", 25, 400, TXT)
    b += icon("sparkles", 44, 238, 24, C3, 2)
    for i, line in enumerate(["Stream processing at scale", "Bulletproof data governance", "Production-grade pipelines"]):
        b += T(80, 257, line, 19, 500, C3, cls=f"cyc c{i+1}")
    return doc(W, H, b, "Macphalen: Data Infrastructure Architect", defs, css)

# ═════════════════════════ SECTION HEADERS ═════════════════════════
def header(idx, ic, title, sub):
    b = (card(0, 0, 900, 68, 18) + tile(18, 14, 40, ic)
         + T(78, 30, f"SECTION {idx:02d}", 11, 500, C1, ls=3) + T(78, 54, title, 24, 700, TXT)
         + T(880, 41, sub, 14, 400, MUTED, "end")
         + f'<rect x="30" y="62" width="840" height="2" rx="1" fill="url(#g)" opacity=".7"/>')
    return doc(900, 68, b, f"{title}: {sub}")

# ══════════════════════════════ ABOUT ══════════════════════════════
def about():
    W, H = 900, 372
    b = card(0, 0, W, H, 22, BG)
    b += icon("hand", 36, 30, 22, C3, 2) + T(68, 47, "HI THERE, I'M MACPHALEN", 13, 500, C1, ls=3)
    b += T(36, 100, "I architect the heavy-duty data", 36, 700, TXT, ls=-.5)
    b += T(36, 144, "infrastructure modern enterprises run on.", 36, 700, "url(#g)", ls=-.5)
    for i, ln in enumerate(["From high-throughput stream processing to bulletproof data governance, I",
                            "engineer scalable, secure, production-grade pipelines that turn raw data",
                            "chaos into an organization's most trusted asset."]):
        b += T(36, 190 + i*26, ln, 17, 400, SOFT)
    cards = [("user", "WHOAMI", "Macphalen", "Infrastructure Architect"),
             ("search", "FOCUS", "Streaming · Governance", "Scalable pipelines"),
             ("flask-conical", "MODE", "Endlessly curious", "Testing new architectures"),
             ("crown", "OFF-KEYBOARD", "Sudoku master", "Serious chess player")]
    cw, gap, y = 202, 16, 262
    for i, (ic, lab, v1, v2) in enumerate(cards):
        x = 24 + i*(cw+gap) - (0)
        b += card(x, y, cw, 92, 16) + tile(x+14, y+14, 34, ic)
        b += T(x+58, y+36, lab, 11, 500, C1, ls=2.5)
        b += T(x+16, y+70, v1, 15, 700, TXT) + T(x+16, y+86, v2, 12, 400, MUTED)
    return doc(W, H, b, "About Macphalen")

# ═════════════════════════════ PIPELINE ═════════════════════════════
def pipeline():
    W, H = 900, 290
    css = (".flow{stroke-dasharray:6 8;animation:flow 1s linear infinite}@keyframes flow{to{stroke-dashoffset:-14}}"
           ".pulse{animation:p 2.4s ease-in-out infinite;transform-origin:810px 100px}@keyframes p{50%{opacity:.35}}")
    defs = '<filter id="glow"><feGaussianBlur stdDeviation="3"/></filter>'
    b = card(0, 0, W, H, 22, BG)
    b += (f'<line x1="126" y1="100" x2="774" y2="100" stroke="#fff" stroke-opacity=".1" stroke-width="2"/>'
          f'<line class="flow" x1="126" y1="100" x2="774" y2="100" stroke="url(#g)" stroke-width="2"/>')
    nodes = [("waves", "Raw data", "Chaos"), ("radio-tower", "Ingest", "Kafka · APIs"),
             ("cog", "Process", "Stream & batch"), ("shield-check", "Govern", "Quality · Lineage"),
             ("database", "Store", "SQL · NoSQL"), ("badge-check", "Trusted", "FastAPI · Grafana")]
    for i, (ic, name, sub) in enumerate(nodes):
        cx = 90 + i*144
        if i == 5:
            b += f'<circle class="pulse" cx="{cx}" cy="100" r="52" fill="url(#g)" opacity=".28" filter="url(#glow)"/>'
            b += tile(cx-38, 62, 76, ic)
        elif i == 0:
            b += (f'<rect x="{cx-38}" y="62" width="76" height="76" rx="23" fill="rgba(255,95,109,.12)" stroke="{C2}" stroke-opacity=".5" stroke-dasharray="4 5"/>'
                  + icon(ic, cx-17, 83, 34, C2, 2))
        else:
            b += tile(cx-38, 62, 76, ic, grad=False, color=C3, tint=CARD)
        b += T(cx, 172, name, 17, 700, TXT, "middle") + T(cx, 193, sub, 12.5, 400, MUTED, "middle")
    for i in range(3):
        b += (f'<circle r="5" fill="{C3}" filter="url(#glow)"><animateMotion dur="6s" begin="{i*2}s" repeatCount="indefinite" path="M126 100 H774"/></circle>'
              f'<circle r="3" fill="#fff"><animateMotion dur="6s" begin="{i*2}s" repeatCount="indefinite" path="M126 100 H774"/></circle>')
    b += (f'<rect x="60" y="238" width="780" height="4" rx="2" fill="url(#g)" opacity=".85"/>'
          + T(60, 268, "ENTROPY", 11.5, 500, C2, ls=3) + T(840, 268, "TRUST", 11.5, 500, C3, "end", ls=3)
          + T(450, 268, "every stage makes the data more reliable", 12.5, 400, MUTED, "middle"))
    return doc(W, H, b, "Data pipeline: raw data, ingest, process, govern, store, trusted", defs, css)

# ═════════════════════════════ PRINCIPLES ═════════════════════════════
def principles():
    W, H = 900, 186
    items = [("shield-check", "Reliable", "Pipelines that fail loudly", "and recover gracefully."),
             ("trending-up", "Scalable", "Designed for 10× growth,", "not today's volume."),
             ("lock", "Governed", "Quality, lineage & access", "built in, not bolted on."),
             ("activity", "Observable", "If it isn't measured,", "it isn't production.")]
    cw, gap = 207, 24
    b = ""
    for i, (ic, t, l1, l2) in enumerate(items):
        x = i*(cw+gap) - 0
        b += card(x, 0, cw, H, 20) + tile(x+20, 20, 46, ic)
        b += T(x+84, 40, f"0{i+1}", 12, 500, C1, ls=3)
        b += T(x+20, 108, t, 22, 700, TXT) + T(x+20, 138, l1, 14, 400, SOFT) + T(x+20, 158, l2, 14, 400, SOFT)
    return doc(W, H, b, "Principles: reliable, scalable, governed, observable")

# ═════════════════════════════ STACK LABELS ═════════════════════════════
def stack_label(ic, text, w_est):
    pw = w_est
    b = (f'<line x1="0" y1="22" x2="900" y2="22" stroke="url(#g)" stroke-opacity=".35"/>'
         f'<rect x="{450-pw/2}" y="2" width="{pw}" height="40" rx="20" fill="{BG}" stroke="{BORDER}"/>'
         + icon(ic, 450-pw/2+18, 12, 20, C3, 2) + T(450-pw/2+46, 28, text, 14, 500, TXT, ls=1.5))
    return doc(900, 44, b, text)

# ═════════════════════════════ OFF THE KEYBOARD ═════════════════════════════
def offkeyboard():
    W, H = 900, 330
    css = (".pl{animation:pl 2.2s ease-in-out infinite}@keyframes pl{50%{opacity:.35}}"
           ".flow{stroke-dasharray:7 7;animation:flow 1s linear infinite}@keyframes flow{to{stroke-dashoffset:-14}}")
    b = ""
    # chess card
    cx0 = 0
    b += card(cx0, 0, 442, 240, 22, BG) + card(458, 0, 442, 240, 22, BG)
    bx, by, cs = cx0+26, 32, 22
    for r in range(8):
        for c in range(8):
            col = "#2b3342" if (r+c) % 2 == 0 else "#171d28"
            b += f'<rect x="{bx+c*cs}" y="{by+r*cs}" width="{cs}" height="{cs}" fill="{col}"/>'
    def cc(c, r): return bx + c*cs + cs/2, by + r*cs + cs/2
    sx, sy = cc(6, 7); mx, my = cc(6, 5); ex, ey = cc(5, 5)
    b += f'<rect class="pl" x="{bx+6*cs}" y="{by+7*cs}" width="{cs}" height="{cs}" fill="{C2}" opacity=".75"/>'
    b += f'<rect class="pl" x="{bx+5*cs}" y="{by+5*cs}" width="{cs}" height="{cs}" fill="{C3}" opacity=".75" style="animation-delay:-1.1s"/>'
    b += f'<path class="flow" d="M{sx} {sy} L{mx} {my} L{ex} {ey}" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
    b += f'<rect x="{bx-.5}" y="{by-.5}" width="{8*cs+1}" height="{8*cs+1}" fill="none" stroke="{C1}" stroke-opacity=".5"/>'
    tx = cx0 + 232
    b += tile(tx, 32, 42, "crown") + T(tx, 108, "THE BOARD", 11, 500, C1, ls=3)
    b += T(tx, 144, "Chess", 34, 700, TXT) + T(tx, 172, "Pattern recognition", 15, 400, SOFT) + T(tx, 192, "under pressure.", 15, 400, SOFT)
    # sudoku card
    ox = 458
    gx, gy, sc = ox+26, 32, 175.5/9
    puzzle = ["53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1", "7...2...6", ".6....28.", "...419..5", "....8..79"]
    b += f'<rect x="{gx}" y="{gy}" width="{9*sc}" height="{9*sc}" fill="#171d28"/>'
    b += f'<rect x="{gx}" y="{gy+4*sc}" width="{9*sc}" height="{sc}" fill="{C1}" opacity=".10"/><rect x="{gx+4*sc}" y="{gy}" width="{sc}" height="{9*sc}" fill="{C1}" opacity=".10"/>'
    b += f'<rect class="pl" x="{gx+4*sc}" y="{gy+4*sc}" width="{sc}" height="{sc}" fill="{C3}" opacity=".8"/>'
    for i in range(10):
        thick = i % 3 == 0
        sw, op = (1.6, .7) if thick else (.6, .35)
        b += (f'<line x1="{gx+i*sc}" y1="{gy}" x2="{gx+i*sc}" y2="{gy+9*sc}" stroke="{C1}" stroke-width="{sw}" stroke-opacity="{op}"/>'
              f'<line x1="{gx}" y1="{gy+i*sc}" x2="{gx+9*sc}" y2="{gy+i*sc}" stroke="{C1}" stroke-width="{sw}" stroke-opacity="{op}"/>')
    for r, row in enumerate(puzzle):
        for c, ch in enumerate(row):
            if ch != ".":
                b += T(gx+c*sc+sc/2, gy+r*sc+sc/2+4.5, ch, 13, 500, TXT, "middle")
    b += T(gx+4*sc+sc/2, gy+4*sc+sc/2+5, "?", 14, 700, BG, "middle")
    tx = ox + 232
    b += tile(tx, 32, 42, "grid-3x3") + T(tx, 108, "THE GRID", 11, 500, C1, ls=3)
    b += T(tx, 144, "Sudoku", 34, 700, TXT) + T(tx, 172, "Constraint solving,", 15, 400, SOFT) + T(tx, 192, "one cell at a time.", 15, 400, SOFT)
    # quote strip
    b += card(0, 258, W, 72, 18, CARD) + icon("puzzle", 30, 280, 28, C3, 2)
    b += T(76, 288, "Chess trains pattern recognition. Sudoku trains constraint satisfaction.", 17, 400, SOFT)
    b += T(76, 312, "Data engineering needs both.", 17, 700, "url(#g)")
    return doc(W, H, b, "Off the keyboard: chess and sudoku", "", css)

# ═════════════════════════════ CURRENTLY ═════════════════════════════
def currently():
    W, H = 900, 176
    items = [("telescope", "EXPLORING", "The data frontier", "New tools, concepts and advanced", "architectures across the data space."),
             ("wrench", "SHARPENING", "Stream processing", "Real-time pipelines and data", "governance, at enterprise scale."),
             ("target", "AIMING FOR", "Trusted pipelines", "Production-grade systems people", "can depend on, every single day.")]
    cw, gap = 284, 24
    b = ""
    for i, (ic, lab, t, l1, l2) in enumerate(items):
        x = i*(cw+gap)
        b += card(x, 0, cw, H, 20) + tile(x+20, 20, 44, ic) + T(x+78, 48, lab, 11.5, 500, C1, ls=3)
        b += T(x+20, 108, t, 21, 700, TXT) + T(x+20, 136, l1, 13.5, 400, SOFT) + T(x+20, 155, l2, 13.5, 400, SOFT)
    return doc(W, H, b, "Currently: exploring, sharpening, aiming for")

# ═════════════════════════════ BUTTONS ═════════════════════════════
GH_PATH = ("M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z")
LI_ICON = ('<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>'
           '<rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/>')

def button(label, kind):
    W, H = 210, 56
    css = ".bd{stroke-dasharray:6 6;animation:d 2s linear infinite}@keyframes d{to{stroke-dashoffset:-24}}"
    b = (f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="28" fill="{BG}" stroke="url(#g)" stroke-width="1.6"/>')
    ix, iy = 26, 16
    if kind == "github":
        b += f'<g transform="translate({ix} {iy}) scale(1.5)" fill="{C3}"><path d="{GH_PATH}"/></g>'
    elif kind == "linkedin":
        b += f'<g transform="translate({ix} {iy}) scale(1)" fill="none" stroke="{C3}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{LI_ICON}</g>'
    else:
        b += icon("mail", ix, iy, 24, C3, 2)
    b += T(64, 34, label, 17, 700, TXT)
    return doc(W, H, b, label, "", css, (700,))

# ═════════════════════════════ FOOTER ═════════════════════════════
def footer():
    W, H = 900, 260
    css = (".ln{opacity:0;animation:ln 12s infinite}.l2{animation-delay:3s}.l3{animation-delay:6s}.l4{animation-delay:9s}"
           "@keyframes ln{0%{opacity:0;transform:translateY(10px)}3%,22%{opacity:1;transform:translateY(0)}27%,100%{opacity:0;transform:translateY(-10px)}}")
    def wave(base, amp, ph, op, dur, fill):
        pts = [f"{x},{base + amp*math.sin(2*math.pi*x/450 + ph):.1f}" for x in range(0, 1801, 15)]
        return (f'<path d="M{" L".join(pts)} L1800,{H} L0,{H} Z" fill="{fill}" opacity="{op}">'
                f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-450 0" dur="{dur}s" repeatCount="indefinite"/></path>')
    defs = f'<clipPath id="cl"><rect width="{W}" height="{H}" rx="26"/></clipPath>'
    b = f'<rect width="{W}" height="{H}" rx="26" fill="{BG}"/><g clip-path="url(#cl)">'
    b += wave(200, 10, 0, .30, 11, "url(#g)") + wave(214, 9, 2, .55, 8, "url(#g)") + wave(230, 7, 4, 1, 6, "url(#g)")
    b += '</g>' + f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="26" fill="none" stroke="{BORDER}"/>'
    b += icon("zap", 450-12, 28, 24, C3, 2)
    lines = [("Data is the new oil.", TXT), ("…but I build the refineries.", "url(#g)"), ("Thanks for visiting.", TXT), ("Have an awesome day!", "url(#g)")]
    for i, (s, f) in enumerate(lines):
        b += T(450, 106, s, 40, 700, f, "middle", -1, cls=f"ln l{i+1}")
    b += T(450, 150, "Got a messy data problem? Let's talk.", 17, 400, SOFT, "middle")
    return doc(W, H, b, "Data is the new oil, but I build the refineries", defs, css)

# ═════════════════════════════ STATS (live) ═════════════════════════════
QUERY = """query($login:String!){user(login:$login){
 followers{totalCount}
 pullRequests{totalCount} issues{totalCount}
 repositories(ownerAffiliations:OWNER,isFork:false,first:100,orderBy:{field:STARGAZERS,direction:DESC}){
   totalCount nodes{stargazerCount languages(first:6,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}
 contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount date}}}}}}"""

def fetch():
    tok = os.environ.get("GH_TOKEN")
    if not tok: return None
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {tok}", "Content-Type": "application/json", "User-Agent": "profile-stats"})
    u = json.load(urllib.request.urlopen(req))["data"]["user"]
    days = [d for w in u["contributionsCollection"]["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    langs = {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    tot = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
    cur = 0
    seq = [d["contributionCount"] for d in days]
    for i, c in enumerate(reversed(seq)):
        if c > 0: cur += 1
        elif i == 0: continue
        else: break
    best = run = 0
    for c in seq:
        run = run + 1 if c > 0 else 0
        best = max(best, run)
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"][-26:]
    return dict(stars=sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
                contribs=u["contributionsCollection"]["contributionCalendar"]["totalContributions"],
                prs=u["pullRequests"]["totalCount"], issues=u["issues"]["totalCount"],
                repos=u["repositories"]["totalCount"], followers=u["followers"]["totalCount"],
                langs=[(n, v/tot*100) for n, v in top], cur=cur, best=best,
                weeks=[[d["contributionCount"] for d in w["contributionDays"]] for w in weeks])

def stats(d=None):
    W, H = 900, 520
    fmt = (lambda v: f"{v:,}") if d else (lambda v: "–")
    b = card(0, 0, W, H, 22, BG)
    tiles = [("star", "STARS", d and d["stars"]), ("git-commit-horizontal", "CONTRIBUTIONS · 1Y", d and d["contribs"]),
             ("git-pull-request", "PULL REQUESTS", d and d["prs"]), ("circle-dot", "ISSUES", d and d["issues"]),
             ("book-marked", "REPOSITORIES", d and d["repos"]), ("users", "FOLLOWERS", d and d["followers"])]
    for i, (ic, lab, v) in enumerate(tiles):
        x, y = 24 + (i % 3)*192, 24 + (i // 3)*114
        b += card(x, y, 176, 98, 16) + icon(ic, x+16, y+16, 18, C3, 2) + T(x+42, y+30, lab, 10.5, 500, MUTED, ls=1.8)
        b += T(x+16, y+78, fmt(v) if d else "–", 36, 700, TXT)
    # languages
    px = 608
    b += card(px, 24, 268, 212, 16) + icon("code-xml", px+16, 38, 18, C3, 2) + T(px+42, 52, "TOP LANGUAGES", 10.5, 500, MUTED, ls=1.8)
    pal = [C2, C3, C1, "#f58fb0", "#a79bff"]
    if d and d["langs"]:
        for i, (n, p) in enumerate(d["langs"]):
            y = 78 + i*30
            b += T(px+16, y+10, n, 13, 500, TXT) + T(px+252, y+10, f"{p:.1f}%", 12, 400, MUTED, "end")
            b += f'<rect x="{px+16}" y="{y+17}" width="236" height="5" rx="2.5" fill="#1f2631"/><rect x="{px+16}" y="{y+17}" width="{max(236*p/100,3):.1f}" height="5" rx="2.5" fill="{pal[i%5]}"/>'
    else:
        b += T(px+134, 140, "Awaiting first workflow run", 13, 400, MUTED, "middle")
    # streak + heatmap
    b += card(24, 252, 852, 232, 16)
    b += icon("flame", 48, 274, 20, C2, 2) + T(76, 290, "CONTRIBUTION STREAK", 10.5, 500, MUTED, ls=1.8)
    cols = [("CURRENT", d and d["cur"], "url(#g)"), ("LONGEST", d and d["best"], TXT)]
    for i, (lab, v, f) in enumerate(cols):
        x = 48 + i*140
        b += T(x, 340, lab, 10.5, 500, C1, ls=2) + T(x, 392, str(v) if d else "–", 52, 700, f) + T(x, 416, "days", 13, 400, MUTED)
    b += T(48, 456, "Past-year total", 11, 500, MUTED, ls=1.5) + T(168, 456, fmt(d["contribs"]) if d else "–", 14, 700, TXT)
    hx, hy, cs, gp = 360, 306, 16, 3.5
    b += T(hx, 290, "LAST 26 WEEKS", 10.5, 500, MUTED, ls=1.8)
    weeks = d["weeks"] if d else [[0]*7]*26
    mx = max([c for w in weeks for c in w] + [1])
    lv = ["#1b212b", "#4a2633", "#8c3446", "#d04559", C2]
    for wi, w in enumerate(weeks):
        for di, c in enumerate(w):
            l = 0 if c == 0 else min(4, 1 + int(3*c/mx))
            b += f'<rect x="{hx+wi*(cs+gp):.1f}" y="{hy+di*(cs+gp):.1f}" width="{cs}" height="{cs}" rx="4" fill="{lv[l]}"/>'
    lx = hx + 26*(cs+gp) - 5*(cs+gp) - 80
    b += T(lx+0, 460, "LESS", 10, 500, MUTED, "end", 1.5)
    for i, c in enumerate(lv):
        b += f'<rect x="{lx+10+i*19}" y="450" width="14" height="14" rx="4" fill="{c}"/>'
    b += T(lx+10+5*19+8, 460, "MORE", 10, 500, MUTED, ls=1.5)
    foot = f"Updated {date.today().isoformat()} · auto-generated by GitHub Actions" if d else "Run the “Profile stats” workflow to fill this in"
    b += T(450, 508, foot, 11.5, 400, MUTED, "middle")
    return doc(W, H, b, f"GitHub stats for {USER}")

# ═════════════════════════════ MAIN ═════════════════════════════
def build_static():
    print("Generating assets/")
    save("hero.svg", hero())
    heads = [("about", 1, "user", "About me", "who I am"), ("pipeline", 2, "workflow", "How I think about data", "from chaos to trust"),
             ("arsenal", 3, "toolbox", "Tech arsenal", "tools of the trade"), ("stats", 4, "trending-up", "By the numbers", "live from GitHub"),
             ("snake", 5, "activity", "The snake devours my contributions", "play it, watch it eat"),
             ("offkeyboard", 6, "crown", "Off the keyboard", "chess · sudoku"), ("currently", 7, "telescope", "Currently", "what's on my radar"),
             ("connect", 8, "mail", "Let's connect", "say hello")]
    for key, i, ic, t, s in heads:
        save(f"h-{key}.svg", header(i, ic, t, s))
    save("about.svg", about()); save("pipeline.svg", pipeline()); save("principles.svg", principles())
    save("stack-1.svg", stack_label("database", "LANGUAGES & DATABASES", 330))
    save("stack-2.svg", stack_label("radio-tower", "DATA, STREAMING & OBSERVABILITY", 420))
    save("stack-3.svg", stack_label("cloud", "CLOUD & DEVOPS", 250))
    save("stack-4.svg", stack_label("toolbox", "DAILY DRIVERS", 240))
    save("offkeyboard.svg", offkeyboard()); save("currently.svg", currently())
    save("btn-linkedin.svg", button("LinkedIn", "linkedin")); save("btn-email.svg", button("Email me", "email")); save("btn-github.svg", button("Follow", "github"))
    save("footer.svg", footer())
    if not os.path.exists(os.path.join(ASSETS, "stats.svg")):
        save("stats.svg", stats(None))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        data = fetch()
        if data is None: sys.exit("GH_TOKEN not set")
        save("stats.svg", stats(data))
    else:
        build_static()
