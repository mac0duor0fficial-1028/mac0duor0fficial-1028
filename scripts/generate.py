#!/usr/bin/env python3
"""
Generates every SVG used by README.md (teal minimalist theme) (all text is set in Space Grotesk,
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
BG, CARD, BORDER = "#071a1c", "#0c2427", "#17393d"
TXT, SOFT, MUTED = "#e9fbf8", "#a9cdc9", "#6f9a96"
C1, C2, C3 = "#5eead4", "#2dd4bf", "#14b8a6"

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
def para(x, y, parts, size=16, fill=SOFT, lh=26):
    """parts: list of lines; each line is a list of (text, highlight) tuples."""
    out = ""
    for i, line in enumerate(parts):
        spans = "".join(
            f'<tspan fill="{C1}" font-weight="500">{html.escape(t, quote=False)}</tspan>' if hl
            else f'<tspan>{html.escape(t, quote=False)}</tspan>' for t, hl in line)
        out += f'<text x="{x}" y="{y + i*lh}" font-size="{size}" fill="{fill}">{spans}</text>'
    return out

def hero():
    W, H = 900, 388
    defs = ('<radialGradient id="rg" cx="1" cy="0" r="1"><stop offset="0" stop-color="#2dd4bf" stop-opacity=".22"/>'
            '<stop offset="1" stop-color="#2dd4bf" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="cl"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
    css = (".cur{animation:cur 1.1s steps(1) infinite}@keyframes cur{50%{opacity:0}}"
           ".dot{animation:dot 2.4s ease-in-out infinite}@keyframes dot{50%{opacity:.3}}")
    b = f'<rect width="{W}" height="{H}" rx="22" fill="{BG}"/>'
    b += f'<g clip-path="url(#cl)"><rect width="{W}" height="{H}" fill="url(#rg)"/></g>'
    b += f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="22" fill="none" stroke="{BORDER}"/>'
    b += icon("hand", 44, 40, 22, C1, 2) + T(76, 57, "HELLO THERE!", 13, 500, C1, ls=3.5)
    b += f'<circle class="dot" cx="{W-48}" cy="50" r="4" fill="{C2}"/>'
    b += T(42, 126, "Macphalen", 60, 700, TXT, ls=-1.5)
    b += T(44, 160, "Data Infrastructure Architect", 21, 500, C1)
    b += f'<rect x="352" y="146" width="12" height="3" fill="{C1}" class="cur"/>' if False else ""
    b += f'<line x1="44" y1="188" x2="856" y2="188" stroke="{BORDER}"/><rect x="44" y="187" width="72" height="2" rx="1" fill="url(#g)"/>'
    b += T(44, 234, "I architect the heavy-duty data infrastructure", 28, 700, TXT, ls=-.3)
    b += T(44, 268, "that modern enterprises run on.", 28, 700, "url(#g)", ls=-.3)
    b += para(44, 308, [[("From massive ", 0), ("stream processing", 1), (" to bulletproof ", 0), ("data governance", 1), (", I engineer", 0)],
                        [("scalable, secure, and production-grade pipelines that turn raw data chaos", 0)],
                        [("into an organization's most trusted asset.", 0)]], 16, SOFT, 25)
    return doc(W, H, b, "Hello there! Macphalen, Data Infrastructure Architect. I architect the heavy-duty data infrastructure that modern enterprises run on.", defs, css)

# ═════════════════════════ SECTION HEADERS ═════════════════════════
def header(ic, title, sub):
    b = (card(0, 0, 900, 52, 14) + icon(ic, 20, 14, 24, C1, 2)
         + T(58, 33, title, 19, 700, TXT) + T(880, 32, sub, 13, 400, MUTED, "end"))
    return doc(900, 52, b, f"{title}: {sub}", weights=(400, 700))

# ══════════════════════════════ ABOUT ══════════════════════════════
def about():
    W, H = 900, 178
    items = [("search", "TECHNICAL FOCUS", ["Endlessly curious about the data space,", "constantly exploring new concepts, tools,", "and advanced architectures."]),
             ("crown", "INTERESTS", ["Off the keyboard, I am a Sudoku master and", "a serious chess player. Solving puzzles is", "just what I do, on and off the board."])]
    cw, gap = 438, 24
    b = ""
    for i, (ic, lab, lines) in enumerate(items):
        x = i*(cw+gap)
        b += card(x, 0, cw, H, 18) + tile(x+22, 22, 40, ic, grad=False, color=C1, tint="rgba(45,212,191,.08)", sw=2)
        b += T(x+76, 48, lab, 12, 500, C1, ls=3)
        for j, ln in enumerate(lines):
            b += T(x+22, 98 + j*24, ln, 15.5, 400, SOFT)
    return doc(W, H, b, "About me: technical focus and interests")

# ═════════════════════════════ BUTTONS ═════════════════════════════
GH_PATH = ("M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z")
LI_ICON = ('<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>'
           '<rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/>')

def button(label, kind):
    W, H = 200, 52
    b = f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="26" fill="{CARD}" stroke="{C2}" stroke-opacity=".55" stroke-width="1.4"/>'
    ix, iy = 26, 14
    if kind == "github":
        b += f'<g transform="translate({ix} {iy+1}) scale(1.4)" fill="{C1}"><path d="{GH_PATH}"/></g>'
    elif kind == "linkedin":
        b += f'<g transform="translate({ix} {iy}) scale(1)" fill="none" stroke="{C1}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{LI_ICON}</g>'
    else:
        b += icon("mail", ix, iy, 24, C1, 2)
    b += T(64, 32, label, 16, 700, TXT)
    return doc(W, H, b, label, weights=(700,))

# ═════════════════════════════ FOOTER ═════════════════════════════
def footer():
    W, H = 900, 200
    css = (".ln{opacity:0;animation:ln 12s infinite}.l2{animation-delay:3s}.l3{animation-delay:6s}.l4{animation-delay:9s}"
           "@keyframes ln{0%{opacity:0;transform:translateY(8px)}3%,22%{opacity:1;transform:translateY(0)}27%,100%{opacity:0;transform:translateY(-8px)}}")
    def wave(base, amp, ph, op, dur):
        pts = [f"{x},{base + amp*math.sin(2*math.pi*x/450 + ph):.1f}" for x in range(0, 1801, 15)]
        return (f'<path d="M{" L".join(pts)}" fill="none" stroke="url(#g)" stroke-width="1.6" opacity="{op}">'
                f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-450 0" dur="{dur}s" repeatCount="indefinite"/></path>')
    defs = f'<clipPath id="cl"><rect width="{W}" height="{H}" rx="22"/></clipPath>'
    b = f'<rect width="{W}" height="{H}" rx="22" fill="{BG}"/><g clip-path="url(#cl)">'
    b += wave(162, 7, 0, .25, 12) + wave(172, 6, 2, .45, 9) + wave(182, 5, 4, .9, 7) + '</g>'
    b += f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="22" fill="none" stroke="{BORDER}"/>'
    b += icon("code-xml", 438, 28, 24, C1, 2)
    lines = [("Code. Commit. Repeat.", TXT), ("Welcome to my GitHub universe.", "url(#g)"), ("Thanks for visiting.", TXT), ("Have an awesome day!", "url(#g)")]
    for i, (s_, f) in enumerate(lines):
        b += T(450, 98, s_, 32, 700, f, "middle", -.5, cls=f"ln l{i+1}")
    b += T(450, 132, "Got a messy data problem? Let's talk.", 15, 400, MUTED, "middle")
    return doc(W, H, b, "Code. Commit. Repeat. Thanks for visiting. Have an awesome day!", defs, css)

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
    pal = ["#2dd4bf", "#5eead4", "#14b8a6", "#22d3ee", "#34d399"]
    if d and d["langs"]:
        for i, (n, p) in enumerate(d["langs"]):
            y = 78 + i*30
            b += T(px+16, y+10, n, 13, 500, TXT) + T(px+252, y+10, f"{p:.1f}%", 12, 400, MUTED, "end")
            b += f'<rect x="{px+16}" y="{y+17}" width="236" height="5" rx="2.5" fill="#12333a"/><rect x="{px+16}" y="{y+17}" width="{max(236*p/100,3):.1f}" height="5" rx="2.5" fill="{pal[i%5]}"/>'
    else:
        b += T(px+134, 140, "Awaiting first workflow run", 13, 400, MUTED, "middle")
    # streak + heatmap
    b += card(24, 252, 852, 232, 16)
    b += icon("flame", 48, 274, 20, C1, 2) + T(76, 290, "CONTRIBUTION STREAK", 10.5, 500, MUTED, ls=1.8)
    cols = [("CURRENT", d and d["cur"], "url(#g)"), ("LONGEST", d and d["best"], TXT)]
    for i, (lab, v, f) in enumerate(cols):
        x = 48 + i*140
        b += T(x, 340, lab, 10.5, 500, C1, ls=2) + T(x, 392, str(v) if d else "–", 52, 700, f) + T(x, 416, "days", 13, 400, MUTED)
    b += T(48, 456, "Past-year total", 11, 500, MUTED, ls=1.5) + T(168, 456, fmt(d["contribs"]) if d else "–", 14, 700, TXT)
    hx, hy, cs, gp = 360, 306, 16, 3.5
    b += T(hx, 290, "LAST 26 WEEKS", 10.5, 500, MUTED, ls=1.8)
    weeks = d["weeks"] if d else [[0]*7]*26
    mx = max([c for w in weeks for c in w] + [1])
    lv = ["#0f2a2d", "#115e59", "#0f766e", "#14b8a6", "#5eead4"]
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
    save("h-about.svg", header("user", "About me", "who I am"))
    save("about.svg", about())
    save("h-stack.svg", header("toolbox", "Tech stack", "tools of the trade"))
    save("h-stats.svg", header("trending-up", "GitHub stats", "live from GitHub"))
    save("h-connect.svg", header("mail", "Socials", "say hello"))
    save("btn-linkedin.svg", button("LinkedIn", "linkedin"))
    save("btn-email.svg", button("Email me", "email"))
    save("btn-github.svg", button("Follow", "github"))
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
