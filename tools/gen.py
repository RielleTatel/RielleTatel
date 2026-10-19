"""Generate themed SVG assets for the RielleTatel GitHub profile README.

Palette, type and motifs mirror srielle.netlify.app (src/app/globals.css):
sage light theme + warm-black dark theme, Geist, grid background, pill gradient.
"""
import base64, html, os, re, sys
from fontTools.ttLib import TTFont

W = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(W, "out")
os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)

THEMES = {
    "light": dict(bg="#f5f7f1", fg="#1f3318", muted="#526b4b", accent="#3d5d36",
                  border="rgba(61,93,54,0.16)", grid="rgba(124,155,115,0.22)",
                  card="#ffffff", chip="#e9efe4", g1="#c8d8c1", g2="#7c9b73", g3="#1f3318",
                  chipfg="#1f3318"),
    "dark": dict(bg="#181714", fg="#ffffff", muted="#b2aa9b", accent="#91b086",
                 border="rgba(240,235,224,0.12)", grid="#2a2823",
                 card="#201f1b", chip="#2a2823", g1="#7c9b73", g2="#928b7d", g3="#ffffff",
                 chipfg="#f0ebe0"),
}
MONO_ICONS = {"nextjs", "github", "prisma", "expo", "vercel", "django"}  # black marks: invert on dark

def b64(path, mime=None):
    ext = path.rsplit(".", 1)[-1].lower()
    mime = mime or {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                    "webp": "image/webp", "svg": "image/svg+xml", "woff2": "font/woff2"}[ext]
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()

WEIGHTS = {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold"}
FONT_FILES = {w: os.path.join(W, "fonts", f"{n}.woff2") for w, n in WEIGHTS.items()}
_metrics = {}
def measure(text, size, weight=400, tracking=0.0):
    if weight not in _metrics:
        f = TTFont(FONT_FILES[weight])
        _metrics[weight] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
    cmap, hmtx, upm = _metrics[weight]
    total = 0
    for ch in text:
        g = cmap.get(ord(ch))
        total += hmtx[g][0] if g else upm * 0.5
    return total / upm * size + tracking * size * max(len(text) - 1, 0)

def font_css(weights):
    return "".join(
        f"@font-face{{font-family:'Geist';font-weight:{w};src:url({b64(FONT_FILES[w])}) format('woff2');}}"
        for w in sorted(weights))

def esc(s):
    return html.escape(s, quote=True)

def svg(w, h, body, t, weights=(400, 500, 600, 700), title=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
            f'<title>{esc(title)}</title>'
            f'<style>{font_css(weights)}text{{font-family:Geist,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;}}</style>'
            f'{body}</svg>')

def grid(w, h, t, step=40, r=28, pid="g"):
    return (f'<defs><pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<path d="M {step} 0 L 0 0 0 {step}" fill="none" stroke="{t["grid"]}" stroke-width="1"/></pattern>'
            f'<clipPath id="{pid}c"><rect width="{w}" height="{h}" rx="{r}"/></clipPath></defs>'
            f'<g clip-path="url(#{pid}c)"><rect width="{w}" height="{h}" fill="{t["bg"]}"/>'
            f'<rect width="{w}" height="{h}" fill="url(#{pid})"/></g>'
            f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{r}" fill="none" stroke="{t["border"]}"/>')

def text(x, y, s, size, weight, fill, anchor="start", tracking=0.0, extra=""):
    ls = f' letter-spacing="{tracking*size:.2f}"' if tracking else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{ls} {extra}>{esc(s)}</text>')

def chip(x, y, label, t, size=15, h=34, icon=None, mono=False, dark=False, weight=500):
    pad = 14
    iw = 20 if icon else 0
    gap = 8 if icon else 0
    w = pad * 2 + iw + gap + measure(label, size, weight)
    out = f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="{t["chip"]}" stroke="{t["border"]}"/>'
    if icon:
        filt = ' filter="url(#inv)"' if (mono and dark) else ""
        out += f'<image x="{x+pad}" y="{y+(h-iw)/2}" width="{iw}" height="{iw}" href="{b64(icon)}"{filt}/>'
    out += text(f"{x+pad+iw+gap:.1f}", y + h / 2 + size * 0.36, label, size, weight, t["chipfg"])
    return out, w

INV = '<defs><filter id="inv"><feColorMatrix type="matrix" values="-1 0 0 0 0.94 0 -1 0 0 0.92 0 0 -1 0 0.88 0 0 0 1 0"/></filter></defs>'

# ---------------------------------------------------------------- hero
def hero(t, dark):
    w, h = 1200, 560
    body = grid(w, h, t, pid="hg")
    body += f'<image x="{w/2-95}" y="28" width="190" height="190" href="{b64(os.path.join(W,"img","logo.png"))}"/>'
    lines = ["BUILDING SOFTWARE,", "COMMUNITIES,", "AND OPPORTUNITIES."]
    size, y = 76, 252
    for i, ln in enumerate(lines):
        body += text(w / 2, y + i * 78, ln, size, 700, t["accent"] if i == 2 else t["fg"], "middle", -0.06)
    sub_a = "From web applications to real impactful initiatives, I turn ideas into "
    sub_b = "products."
    sz = 21
    total = measure(sub_a, sz, 400) + measure(sub_b, sz, 600)
    x0 = (w - total) / 2
    body += (f'<text x="{x0:.1f}" y="{y+2*78+58}" font-size="{sz}">'
             f'<tspan font-weight="400" fill="{t["muted"]}">{esc(sub_a)}</tspan>'
             f'<tspan font-weight="600" fill="{t["accent"]}">{esc(sub_b)}</tspan></text>')
    # role pills
    roles = ["Full-Stack Developer", "Speaker", "Student Leader", "ASEAN Delegate"]
    widths = [28 + measure(r, 15, 500) for r in roles]
    gap = 10
    x = (w - (sum(widths) + gap * (len(roles) - 1))) / 2
    py = h - 64
    for r in roles:
        c, cw = chip(x, py, r, t, size=15)
        body += c
        x += cw + gap
    # status + location corners
    body += f'<circle cx="44" cy="46" r="6" fill="{t["accent"]}"/>'
    body += text(60, 51, "Open to opportunities", 14, 500, t["muted"])
    body += text(w - 36, 51, "Zamboanga City, PH", 14, 500, t["muted"], "end")
    return svg(w, h, body, t, title="Gabrielle Tatel — Building software, communities, and opportunities.")

# ---------------------------------------------------------------- section heading
def heading(label, desc, t):
    w, h = 1200, 120
    body = text(4, 64, label, 54, 700, t["fg"], tracking=-0.05)
    lw = measure(label, 54, 700, -0.05)
    body += f'<rect x="{lw+18:.0f}" y="40" width="64" height="26" rx="13" fill="url(#pg)"/>'
    body = (f'<defs><linearGradient id="pg" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{t["g1"]}"/><stop offset=".5" stop-color="{t["g2"]}"/>'
            f'<stop offset="1" stop-color="{t["g3"]}"/></linearGradient></defs>') + body
    body += text(4, 102, desc, 19, 400, t["muted"])
    body += f'<line x1="0" y1="{h-1}" x2="{w}" y2="{h-1}" stroke="{t["border"]}"/>'
    return svg(w, h, body, t, (400, 700), title=label)

# ---------------------------------------------------------------- project card
def wrap(s, size, weight, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if measure(trial, size, weight) <= maxw:
            cur = trial
        else:
            lines.append(cur); cur = wd
    lines.append(cur)
    return lines

def card(p, t, dark):
    w, ch = 600, 380
    h = ch + 250
    pid = "c" + p["id"]
    body = (f'<defs><clipPath id="{pid}"><rect width="{w}" height="{h}" rx="24"/></clipPath>'
            f'<linearGradient id="{pid}g" x1="0" y1="0" x2="1" y2="1">'
            + (f'<stop offset="0" stop-color="#c8d8c1"/><stop offset=".55" stop-color="#7c9b73"/><stop offset="1" stop-color="#1f3318"/>' if not dark else
               f'<stop offset="0" stop-color="#91b086"/><stop offset=".55" stop-color="#3d5d36"/><stop offset="1" stop-color="#1f1e1a"/>')
            + f'</linearGradient>'
            f'<pattern id="{pid}p" width="40" height="40" patternUnits="userSpaceOnUse">'
            f'<path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.18)"/></pattern></defs>')
    body += INV
    body += f'<g clip-path="url(#{pid})"><rect width="{w}" height="{h}" fill="{t["card"]}"/>'
    if p.get("cover"):
        body += f'<image width="{w}" height="{ch}" preserveAspectRatio="xMidYMid slice" href="{b64(os.path.join(W,"img",p["cover"]))}"/>'
    else:
        body += f'<rect width="{w}" height="{ch}" fill="url(#{pid}g)"/><rect width="{w}" height="{ch}" fill="url(#{pid}p)"/>'
        body += text(w / 2, ch / 2 + 6, p["wordmark"], 64, 700, "#ffffff", "middle", -0.05)
        body += text(w / 2, ch / 2 + 46, p["kicker"], 16, 500, "rgba(255,255,255,0.85)", "middle", 0.12)
    body += f'<line x1="0" y1="{ch}" x2="{w}" y2="{ch}" stroke="{t["border"]}"/></g>'
    body += f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="24" fill="none" stroke="{t["border"]}"/>'
    x = 32
    y = ch + 52
    body += text(x, y, p["title"], 30, 700, t["fg"], tracking=-0.03)
    body += text(w - 32, y - 2, "↗", 26, 500, t["muted"], "end")
    for i, ln in enumerate(wrap(p["tagline"], 18, 400, w - 64)[:2]):
        body += text(x, y + 32 + i * 24, ln, 18, 400, t["muted"])
    body += text(x, y + 92, p["impact"], 17, 600, t["accent"])
    cx, cy = x, h - 58
    for s in p["stack"]:
        c, cw = chip(cx, cy, s, t, size=13, h=30)
        if cx + cw > w - 32:
            break
        body += c
        cx += cw + 8
    return svg(w, h, body, t, title=f'{p["title"]} — {p["tagline"]}')

# ---------------------------------------------------------------- experience
def experience(roles, t, dark):
    w, h = 1200, 280
    body = INV
    colw, gap = 384, 24
    for i, r in enumerate(roles):
        x = i * (colw + gap)
        body += f'<rect x="{x+0.5}" y="0.5" width="{colw-1}" height="{h-1}" rx="22" fill="{t["card"]}" stroke="{t["border"]}"/>'
        body += (f'<clipPath id="lg{i}"><rect x="{x+26}" y="26" width="52" height="52" rx="12"/></clipPath>'
                 f'<rect x="{x+26}" y="26" width="52" height="52" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>'
                 f'<image x="{x+26}" y="26" width="52" height="52" clip-path="url(#lg{i})" preserveAspectRatio="xMidYMid slice" href="{b64(os.path.join(W,"img",r["logo"]))}"/>')
        body += text(x + 92, 46, r["company"], 14, 500, t["muted"])
        body += text(x + 92, 72, r["title"], 21, 700, t["fg"], tracking=-0.02)
        body += text(x + 26, 112, r["meta"], 13, 500, t["muted"], tracking=0.04)
        my = 160
        for j, (fig, lab) in enumerate(r["metrics"][:2]):
            yy = my + j * 74
            body += text(x + 26, yy, fig, 36, 700, t["accent"], tracking=-0.04)
            body += text(x + 26, yy + 26, lab, 15, 400, t["muted"])
    return svg(w, h, body, t, title="Experience")

# ---------------------------------------------------------------- stack
def stack(groups, t, dark):
    w, pad, rowh, labw = 1200, 36, 104, 230
    h = pad * 2 + rowh * len(groups) - 8
    body = grid(w, h, t, pid="sg") + INV
    tile, gap = 60, 22
    for i, (label, sub, tools) in enumerate(groups):
        y = pad + i * rowh
        if i:
            body += f'<line x1="{pad}" y1="{y-14}" x2="{w-pad}" y2="{y-14}" stroke="{t["border"]}"/>'
        body += text(pad, y + 30, label, 13, 600, t["accent"], tracking=0.12)
        body += text(pad, y + 52, sub, 14, 400, t["muted"])
        x = pad + labw
        for name, icon in tools:
            cw = max(tile, measure(name, 12, 500) + 4)
            tx = x + (cw - tile) / 2
            body += f'<rect x="{tx}" y="{y}" width="{tile}" height="{tile}" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>'
            filt = ' filter="url(#inv)"' if (icon in MONO_ICONS and dark) else ""
            body += f'<image x="{tx+15}" y="{y+15}" width="30" height="30" href="{b64(os.path.join(W,"img","brand-icons",icon+".svg"))}"{filt}/>'
            body += text(x + cw / 2, y + tile + 20, name, 12, 500, t["muted"], "middle")
            x += cw + gap
    names = ", ".join(n for _, _, tl in groups for n, _ in tl)
    return svg(w, h, body, t, (400, 500, 600), title="Tech stack: " + names)

# ---------------------------------------------------------------- contact
def contact(t, dark):
    w, h = 1200, 300
    body = grid(w, h, t, pid="kg")
    body += text(w / 2, 104, "The goal was never just to code.", 46, 700, t["fg"], "middle", -0.05)
    body += text(w / 2, 158, "The goal was always to create impact.", 46, 700, t["accent"], "middle", -0.05)
    body += text(w / 2, 214, "tatelgabrielle19@gmail.com", 20, 600, t["fg"], "middle")
    body += text(w / 2, 248, "Zamboanga City, Philippines  ·  Mon–Fri, 8:00 AM – 6:00 PM PHT", 16, 400, t["muted"], "middle")
    return svg(w, h, body, t, title="Contact: tatelgabrielle19@gmail.com")

def button(label, icon, t, dark, primary=False):
    size, h = 16, 46
    iw = 20 if icon else 0
    w = 22 * 2 + iw + (10 if icon else 0) + measure(label, size, 600)
    fill = t["fg"] if primary else t["chip"]
    fg = t["bg"] if primary else t["chipfg"]
    body = INV + f'<rect x="0.5" y="0.5" width="{w-1:.1f}" height="{h-1}" rx="{h/2}" fill="{fill}" stroke="{t["border"]}"/>'
    x = 22
    if icon:
        mono = icon in MONO_ICONS
        filt = ' filter="url(#inv)"' if (mono and (dark != primary)) else ""
        body += f'<image x="{x}" y="{(h-iw)/2}" width="{iw}" height="{iw}" href="{b64(os.path.join(W,"img","brand-icons",icon+".svg"))}"{filt}/>'
        x += iw + 10
    body += text(x, h / 2 + size * 0.36, label, size, 600, fg)
    return svg(int(w + 1), h, body, t, (600,), title=label)

# ---------------------------------------------------------------- data
PROJECTS = [
    dict(id="coaz", title="COA-Z", repo="council-of-organizations", cover="coa-z-homepage-v2.webp",
         tagline="Opening more paths into campus life: the official Council of Organizations site and publishing workspace.",
         impact="6,000+ students · 40+ organizations", stack=["React", "TypeScript", "Supabase", "Tiptap"]),
    dict(id="unyon", title="Unyon Mindanao Portal", repo="unyon-mindanao", cover="unyon-mindanao-cover.webp",
         tagline="Making shared administration easier to account for: records, verified invitations, roles, and audit history.",
         impact="8+ member universities", stack=["Next.js", "Cloudflare D1", "Firebase Auth", "R2"]),
    dict(id="autocare", title="AutoCare+", repo="autocare", cover="autocare-cover-v2.webp",
         tagline="Connecting a local shop, its field team, and vehicle owners. Works even when field connectivity drops.",
         impact="1 staff console + 2 mobile apps", stack=["NestJS", "Next.js", "Expo", "PostgreSQL"]),
    dict(id="ambagan", title="Ambagan", repo="ambagan-", wordmark="Ambagan", kicker="STELLAR HACKATHON",
         tagline="The Filipino paluwagan, on-chain. Rotating savings circles and community-approved loans on Stellar.",
         impact="Live at ambagan.site · on-chain AMBPHP asset", stack=["Next.js", "Stellar SDK", "Supabase", "Vitest"]),
    dict(id="osa", title="OSA Activity Tracking", repo="osa-system", wordmark="OSA", kicker="ATENEO DE ZAMBOANGA",
         tagline="Real-time status for student-org activity requests across a 5-stage approval chain. No repeat office visits.",
         impact="~50% faster approvals · 40+ student orgs", stack=["Laravel", "PHP", "Tailwind", "MySQL"]),
    dict(id="debately", title="Debately", repo="debately", wordmark="Debately", kicker="BUILT BY A DEBATER",
         tagline="Debate tournament management, built by a debater.",
         impact="SaaS for debate tournaments", stack=["Next.js", "Supabase", "Prisma", "Tailwind"]),
]
ROLES = [
    dict(company="Symph Inc.", title="Software Developer", logo="symph.jpg",
         meta="MAY – JUL 2026  ·  CEBU CITY", metrics=[("100,000+", "records per XLSX bulk import"), ("Web + mobile", "features shipped, payments hardened")]),
    dict(company="CITS · Ateneo de Zamboanga", title="System Developer", logo="adzu.jpg",
         meta="JUL – SEP 2026  ·  CONTRACT", metrics=[("~50%", "faster approvals"), ("~70%", "less manual encoding")]),
    dict(company="Independent projects", title="Freelance Developer", logo="logo.png",
         meta="FREELANCE  ·  ZAMBOANGA CITY", metrics=[("5+", "clients"), ("3", "products shipped")]),
]
STACK = [
    ("FRONTEND", "Web apps and interfaces", [("Next.js", "nextjs"), ("React", "react"), ("TypeScript", "typescript"),
        ("Tailwind", "tailwindcss"), ("Vite", "vite")]),
    ("BACKEND & DATA", "APIs, auth, and storage", [("Node.js", "nodejs"), ("NestJS", "nestjs"), ("Python", "python"),
        ("Django", "django"), ("PHP", "php"), ("Laravel", "laravel"), ("PostgreSQL", "postgresql"), ("Prisma", "prisma"),
        ("Supabase", "supabase"), ("Firebase", "firebase")]),
    ("MOBILE & INFRA", "Shipping and testing", [("React Native", "react"), ("Expo", "expo"), ("Docker", "docker"),
        ("Cloudflare", "cloudflare"), ("Vitest", "vitest")]),
]
BUTTONS = [("portfolio", "Portfolio ↗", None, True), ("linkedin", "LinkedIn", "linkedin", False),
           ("resume", "Résumé", None, False), ("email", "Email", None, False)]

def write(name, content):
    with open(os.path.join(OUT, "assets", name), "w") as f:
        f.write(content)

for mode, t in THEMES.items():
    dark = mode == "dark"
    write(f"hero-{mode}.svg", hero(t, dark))
    write(f"h-projects-{mode}.svg", heading("Projects.", "Software built for real people, campuses, and communities in Mindanao.", t))
    write(f"h-experience-{mode}.svg", heading("Experience.", "Where I've shipped, and what changed because of it.", t))
    for p in PROJECTS:
        write(f"p-{p['id']}-{mode}.svg", card(p, t, dark))
    write(f"experience-{mode}.svg", experience(ROLES, t, dark))
    write(f"stack-{mode}.svg", stack(STACK, t, dark))
    write(f"contact-{mode}.svg", contact(t, dark))
    for bid, label, icon, primary in BUTTONS:
        write(f"btn-{bid}-{mode}.svg", button(label, icon, t, dark, primary))

# ---------------------------------------------------------------- README
def pic(name, alt, width=None, href=None):
    wa = f' width="{width}"' if width else ""
    s = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">'
         f'<img alt="{esc(alt)}" src="assets/{name}-light.svg"{wa}></picture>')
    return f'<a href="{href}">{s}</a>' if href else s

GH = "https://github.com/RielleTatel/"
SITE = "https://srielle.netlify.app/"
links = {"portfolio": SITE, "linkedin": "https://www.linkedin.com/in/gabrielle-tatel-3b337b2b9/",
         "resume": SITE + "resume/gabrielle-tatel-resume.pdf", "email": "mailto:tatelgabrielle19@gmail.com"}

md = []
md.append(f'<div align="center">\n\n{pic("hero", "Gabrielle Tatel — Building software, communities, and opportunities.", "100%", SITE)}\n')
md.append("<br>\n\n" + "&nbsp;".join(pic(f"btn-{b}", lab, None, links[b]) for b, lab, _, _ in BUTTONS) + "\n\n</div>\n")
md.append("I'm **Gabrielle Tatel**, a full-stack developer and BS Computer Science student at Ateneo de Zamboanga University. "
          "I build software for campuses, local businesses, and communities in Mindanao, and I speak and lead student organizations when I'm not shipping.\n")
md.append(pic("stack", "Tech stack: " + ", ".join(n for _, _, tl in STACK for n, _ in tl), "100%") + "\n")
md.append("<br>\n\n" + pic("h-projects", "Projects", "100%") + "\n\n<p>")
rows = []
for i, p in enumerate(PROJECTS):
    rows.append(pic(f"p-{p['id']}", f'{p["title"]}: {p["tagline"]} ({p["impact"]})', "49%", GH + p["repo"]))
md.append("\n".join(r + ("&nbsp;" if i % 2 == 0 else "<br><br>") for i, r in enumerate(rows)) + "\n</p>\n")
md.append("<br>\n\n" + pic("h-experience", "Experience", "100%") + "\n\n" +
          pic("experience", "Symph Inc. — Software Developer (100,000+ records per bulk import). CITS Ateneo de Zamboanga — System Developer (~50% faster approvals, ~70% less manual encoding). Freelance — 5+ clients, 3 products shipped.", "100%") + "\n")
md.append("<br>\n\n" + pic("contact", "Contact: tatelgabrielle19@gmail.com", "100%", links["email"]) + "\n")
with open(os.path.join(OUT, "README.md"), "w") as f:
    f.write("\n".join(md))
print("done", OUT)
