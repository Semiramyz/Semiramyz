#!/usr/bin/env python3
"""
Genera los recursos visuales del perfil de GitHub.

Uso:
    python scripts/profile_assets.py metrics   # métricas (solo librería estándar; lo ejecuta la GitHub Action)
    python scripts/profile_assets.py static    # encabezado, títulos y tarjetas (requiere: pip install fonttools brotli)

Variables de entorno:
    GH_USER        usuario de GitHub (por defecto: Semiramyz)
    GITHUB_TOKEN   token para la API (en la Action se usa el GITHUB_TOKEN automático)
"""
import base64
import datetime as dt
import json
import os
import sys
import urllib.request
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"
USER = os.environ.get("GH_USER", "Semiramyz")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
TZ = dt.timezone(dt.timedelta(hours=-5))  # Colombia (UTC−5, sin horario de verano)

# ─── Paleta ────────────────────────────────────────────────────────────────
BG = "#0D0D0D"
BORDER = "#3B0A0A"
CRIMSON = "#B3001B"
CRIMSON_LIGHT = "#E23A4E"
BLOOD = "#8B0000"
BONE = "#E8D5C4"
TEXT = "#B8A89C"
MUTED = "#7A6A5E"
LANG_COLORS = ["#B3001B", "#E23A4E", "#8B0000", "#D4C5B0", "#9E6B63", "#C98A7D", "#5E0B12", "#6B5A55"]
HEAT = ["#1C1616", "#4A0A0F", "#7A0E17", "#B3001B", "#E23A4E"]
DAYS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MONTHS_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


# ─── Utilidades SVG ────────────────────────────────────────────────────────
def font_css(*names):
    faces = {
        "bebas": ("Bebas", "BebasNeue.woff2", 400),
        "mono": ("Mono", "JetBrainsMono-Regular.woff2", 400),
        "monob": ("Mono", "JetBrainsMono-Bold.woff2", 700),
    }
    css = []
    for n in names:
        fam, file, w = faces[n]
        data = base64.b64encode((FONTS / file).read_bytes()).decode()
        css.append(
            f"@font-face{{font-family:'{fam}';font-weight:{w};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}"
        )
    css.append(".b{font-family:'Bebas','Impact','Arial Narrow',sans-serif;letter-spacing:1px}")
    css.append(".m{font-family:'Mono','Consolas','Courier New',monospace}")
    return "".join(css)


def svg_doc(w, h, body, fonts=("bebas", "mono", "monob"), extra_css="", title=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>'
        f"<style>{font_css(*fonts)}{extra_css}</style>{body}</svg>"
    )


def card_frame(w, h):
    return (
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>'
        f'<defs><linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{CRIMSON}"/>'
        f'<stop offset="1" stop-color="{CRIMSON}" stop-opacity="0"/></linearGradient></defs>'
    )


def card_title(w, title, right=""):
    s = f'<text x="24" y="40" class="b" font-size="26" fill="{BONE}">{escape(title)}</text>'
    if right:
        s += f'<text x="{w-24}" y="38" class="m" font-size="11" fill="{MUTED}" text-anchor="end">{escape(right)}</text>'
    s += f'<rect x="24" y="52" width="{w-48}" height="1.5" fill="url(#ln)"/>'
    return s


def fmt(n):
    return f"{n:,}".replace(",", ".")


def write(name, content):
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / name).write_text(content, encoding="utf-8")
    print(f"  ✓ assets/{name}")


# ─── API de GitHub ─────────────────────────────────────────────────────────
def api(url, data=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": f"{USER}-profile-metrics"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


GRAPHQL = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        name
        stargazerCount
        languages(first: 20, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}"""


def fetch_data():
    """Devuelve un diccionario con todo lo necesario para las tarjetas."""
    d = {"repos": [], "stars": 0, "langs": Counter(), "calendar": None, "totals": None, "hours": Counter()}

    if TOKEN:
        res = api("https://api.github.com/graphql", {"query": GRAPHQL, "variables": {"login": USER}})
        if "errors" in res:
            raise RuntimeError(res["errors"])
        u = res["data"]["user"]
        repos = u["repositories"]["nodes"]
        d["repos"] = [r["name"] for r in repos]
        d["stars"] = sum(r["stargazerCount"] for r in repos)
        for r in repos:
            for e in r["languages"]["edges"]:
                d["langs"][e["node"]["name"]] += e["size"]
        cc = u["contributionsCollection"]
        d["calendar"] = [day for w in cc["contributionCalendar"]["weeks"] for day in w["contributionDays"]]
        d["totals"] = {
            "contrib": cc["contributionCalendar"]["totalContributions"],
            "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
            "prs": cc["totalPullRequestContributions"],
            "issues": cc["totalIssueContributions"],
        }
    else:  # sin token: solo datos REST públicos (útil para pruebas locales)
        repos = [r for r in api(f"https://api.github.com/users/{USER}/repos?per_page=100") if not r["fork"]]
        d["repos"] = [r["name"] for r in repos]
        d["stars"] = sum(r["stargazers_count"] for r in repos)
        for r in repos:
            for lang, size in api(f"https://api.github.com/repos/{USER}/{r['name']}/languages").items():
                d["langs"][lang] += size

    # Commits por hora (rama principal de cada repositorio propio)
    for name in d["repos"]:
        for page in range(1, 11):
            try:
                commits = api(
                    f"https://api.github.com/repos/{USER}/{name}/commits?author={USER}&per_page=100&page={page}"
                )
            except Exception:
                break
            for c in commits:
                when = dt.datetime.fromisoformat(c["commit"]["author"]["date"].replace("Z", "+00:00"))
                d["hours"][when.astimezone(TZ).hour] += 1
            if len(commits) < 100:
                break
    return d


def streaks(calendar):
    days = sorted(calendar, key=lambda x: x["date"])
    longest = run = 0
    for day in days:
        run = run + 1 if day["contributionCount"] > 0 else 0
        longest = max(longest, run)
    current = 0
    for i, day in enumerate(reversed(days)):
        if day["contributionCount"] > 0:
            current += 1
        elif i == 0:  # hoy sin contribuciones todavía no rompe la racha
            continue
        else:
            break
    return current, longest


# ─── Tarjetas de métricas ──────────────────────────────────────────────────
def stats_card(d):
    w, h = 420, 214
    cur, best = streaks(d["calendar"]) if d["calendar"] else (0, 0)
    t = d["totals"] or {"contrib": 0, "commits": 0, "prs": 0, "issues": 0}
    items = [
        ("Contribuciones", fmt(t["contrib"])), ("Commits", fmt(t["commits"])),
        ("Pull requests", fmt(t["prs"])), ("Issues", fmt(t["issues"])),
        ("Repos públicos", fmt(len(d["repos"]))), ("Estrellas", fmt(d["stars"])),
        ("Racha actual", f"{cur} día" + ("" if cur == 1 else "s")),
        ("Racha máxima", f"{best} día" + ("" if best == 1 else "s")),
    ]
    body = card_frame(w, h) + card_title(w, "Resumen de actividad", "últimos 12 meses")
    for i, (label, value) in enumerate(items):
        col, row = i % 2, i // 2
        x0 = 24 + col * 196
        y = 88 + row * 34
        body += f'<rect x="{x0}" y="{y-9}" width="6" height="6" fill="{CRIMSON}"/>'
        body += f'<text x="{x0+14}" y="{y}" class="m" font-size="12.5" fill="{TEXT}">{escape(label)}</text>'
        body += (f'<text x="{x0+176}" y="{y}" class="m" font-size="14" font-weight="700" '
                 f'fill="{BONE}" text-anchor="end">{escape(value)}</text>')
    return svg_doc(w, h, body, title="Resumen de actividad en GitHub")


def languages_card(d):
    w, h = 420, 214
    total = sum(d["langs"].values()) or 1
    top = d["langs"].most_common()
    if len(top) > 8:
        top = top[:7] + [("Otros", sum(s for _, s in top[7:]))]
    body = card_frame(w, h) + card_title(w, "Lenguajes más usados", "por volumen de código")
    body += '<defs><clipPath id="bar"><rect x="24" y="70" width="372" height="10" rx="5"/></clipPath></defs>'
    body += f'<g clip-path="url(#bar)"><rect x="24" y="70" width="372" height="10" fill="{BORDER}"/>'
    x = 24.0
    for i, (_, size) in enumerate(top):
        bw = 372 * size / total
        body += f'<rect x="{x:.2f}" y="70" width="{bw + 0.5:.2f}" height="10" fill="{LANG_COLORS[i]}"/>'
        x += bw
    body += "</g>"
    for i, (lang, size) in enumerate(top):
        col, row = i % 2, i // 2
        x0 = 24 + col * 196
        y = 112 + row * 26
        pct = 100 * size / total
        body += f'<circle cx="{x0+5}" cy="{y-4}" r="5" fill="{LANG_COLORS[i]}"/>'
        body += f'<text x="{x0+16}" y="{y}" class="m" font-size="12.5" fill="{BONE}">{escape(lang[:14])}</text>'
        body += (f'<text x="{x0+176}" y="{y}" class="m" font-size="12" fill="{MUTED}" '
                 f'text-anchor="end">{pct:.1f}%</text>')
    if not top:
        body += f'<text x="24" y="120" class="m" font-size="12.5" fill="{MUTED}">Sin datos todavía</text>'
    return svg_doc(w, h, body, title="Lenguajes más usados")


def calendar_card(d):
    w, h = 880, 212
    cal = sorted(d["calendar"] or [], key=lambda x: x["date"])
    total = (d["totals"] or {}).get("contrib", 0)
    body = card_frame(w, h) + card_title(w, "Contribuciones", f"{fmt(total)} en los últimos 12 meses")
    x0, y0, cell, gap = 62, 84, 12, 3
    mx = max([c["contributionCount"] for c in cal] or [0])
    if cal:
        first = dt.date.fromisoformat(cal[0]["date"])
        start = first - dt.timedelta(days=(first.weekday() + 1) % 7)  # semanas empiezan en domingo
        last_month = None
        for c in cal:
            day = dt.date.fromisoformat(c["date"])
            col = (day - start).days // 7
            row = (day.weekday() + 1) % 7
            n = c["contributionCount"]
            lvl = 0 if n == 0 else min(4, 1 + int(3.999 * n / mx)) if mx else 0
            x, y = x0 + col * (cell + gap), y0 + row * (cell + gap)
            body += (f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{HEAT[lvl]}">'
                     f"<title>{n} contribuciones · {day.isoformat()}</title></rect>")
            if day.day <= 7 and row == 0 and day.month != last_month:
                body += (f'<text x="{x}" y="{y0-10}" class="m" font-size="10.5" '
                         f'fill="{MUTED}">{MONTHS_ES[day.month-1]}</text>')
                last_month = day.month
        for r, lab in ((1, "Lun"), (3, "Mié"), (5, "Vie")):
            body += (f'<text x="{x0-10}" y="{y0 + r*(cell+gap) + 10}" class="m" font-size="10.5" '
                     f'fill="{MUTED}" text-anchor="end">{lab}</text>')
    else:
        body += f'<text x="24" y="120" class="m" font-size="12.5" fill="{MUTED}">Sin datos todavía</text>'
    ly = h - 20
    lx = w - 24 - 5 * 15 - 40
    body += f'<text x="{lx-8}" y="{ly+10}" class="m" font-size="10.5" fill="{MUTED}" text-anchor="end">Menos</text>'
    for i, col in enumerate(HEAT):
        body += f'<rect x="{lx + i*15}" y="{ly}" width="{cell}" height="{cell}" rx="2.5" fill="{col}"/>'
    body += f'<text x="{lx + 5*15 + 4}" y="{ly+10}" class="m" font-size="10.5" fill="{MUTED}">Más</text>'
    return svg_doc(w, h, body, title="Calendario de contribuciones")


def hours_card(d):
    w, h = 880, 236
    hours = [d["hours"].get(i, 0) for i in range(24)]
    total = sum(hours)
    body = card_frame(w, h) + card_title(w, "Horario de trabajo", f"commits por hora · UTC−5 · {fmt(total)} commits")
    body += (f'<defs><linearGradient id="bg1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CRIMSON}"/>'
             f'<stop offset="1" stop-color="{BLOOD}" stop-opacity="0.55"/></linearGradient>'
             f'<linearGradient id="bg2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CRIMSON_LIGHT}"/>'
             f'<stop offset="1" stop-color="{CRIMSON}"/></linearGradient></defs>')
    left, right, base, top = 60, w - 36, 176, 78
    slot = (right - left) / 24
    mx = max(hours) or 1
    peak = hours.index(max(hours)) if total else -1
    for frac in (0.5, 1.0):
        gy = base - (base - top) * frac
        body += f'<line x1="{left}" y1="{gy}" x2="{right}" y2="{gy}" stroke="{BORDER}" stroke-dasharray="3 5"/>'
    body += f'<line x1="{left}" y1="{base}" x2="{right}" y2="{base}" stroke="{BORDER}"/>'
    for i, n in enumerate(hours):
        bh = (base - top) * n / mx
        x = left + i * slot + slot * 0.18
        bw = slot * 0.64
        fill = "url(#bg2)" if i == peak else "url(#bg1)"
        if n:
            body += (f'<rect x="{x:.1f}" y="{base-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" fill="{fill}">'
                     f"<title>{i:02d}:00 · {n} commits</title></rect>")
        if i == peak:
            body += (f'<text x="{x+bw/2:.1f}" y="{base-bh-7:.1f}" class="m" font-size="11" font-weight="700" '
                     f'fill="{BONE}" text-anchor="middle">{n}</text>')
        if i % 3 == 0:
            body += (f'<text x="{x+bw/2:.1f}" y="{base+17}" class="m" font-size="10.5" fill="{MUTED}" '
                     f'text-anchor="middle">{i:02d}h</text>')
    # Resumen de uso
    parts = []
    if total:
        parts.append(f"Mayor actividad: {peak:02d}:00–{(peak+1)%24:02d}:00")
        blocks = {"Madrugada": range(0, 6), "Mañana": range(6, 12), "Tarde": range(12, 18), "Noche": range(18, 24)}
        best = max(blocks, key=lambda k: sum(hours[i] for i in blocks[k]))
        share = 100 * sum(hours[i] for i in blocks[best]) / total
        parts.append(f"{best}: {share:.0f}% de los commits")
    if d["calendar"]:
        wd = Counter()
        for c in d["calendar"]:
            wd[dt.date.fromisoformat(c["date"]).weekday()] += c["contributionCount"]
        if sum(wd.values()):
            parts.append(f"Día más activo: {DAYS_ES[wd.most_common(1)[0][0]]}")
    body += (f'<text x="24" y="{h-16}" class="m" font-size="11.5" fill="{TEXT}">'
             f'{escape("   ·   ".join(parts) or "Sin datos todavía")}</text>')
    return svg_doc(w, h, body, title="Horario de trabajo: commits por hora")


def build_metrics(data=None):
    print("Generando métricas…")
    d = data or fetch_data()
    write("metrics-stats.svg", stats_card(d))
    write("metrics-languages.svg", languages_card(d))
    write("metrics-calendar.svg", calendar_card(d))
    write("metrics-hours.svg", hours_card(d))


# ─── Recursos estáticos (encabezado, títulos, tarjetas de proyectos) ───────
def text_width(text, size, file="BebasNeue.woff2", letter_spacing=1.0):
    from fontTools.ttLib import TTFont  # solo se necesita para los recursos estáticos
    f = TTFont(FONTS / file)
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    units = sum(hmtx[cmap[ord(ch)]][0] for ch in text if ord(ch) in cmap)
    return units * size / upm + letter_spacing * len(text)


def header_svg():
    w, h = 1200, 330
    name = "JUAN SEBASTIÁN PINEDA SANTAFÉ"
    slashes = "".join(
        f'<line x1="{x}" y1="-20" x2="{x-190}" y2="{h+20}" stroke="{CRIMSON}" '
        f'stroke-width="{sw}" opacity="{op}"/>'
        for x, sw, op in [(900, 1, .18), (955, 3, .10), (1010, 1, .22), (1070, 6, .07), (1120, 1, .16), (1175, 2, .12), (1240, 1, .2)]
    )
    css = (
        "@keyframes f{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}"
        ".a1{animation:f .9s ease-out both}.a2{animation:f .9s .25s ease-out both}.a3{animation:f .9s .5s ease-out both}"
        "@keyframes p{0%,100%{opacity:1}50%{opacity:.25}}.dot{animation:p 2.2s ease-in-out infinite}"
    )
    body = f"""
<defs>
  <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#050505"/><stop offset=".55" stop-color="#120305"/><stop offset="1" stop-color="#2A0508"/>
  </linearGradient>
  <radialGradient id="glow" cx=".82" cy=".45" r=".55">
    <stop offset="0" stop-color="{CRIMSON}" stop-opacity=".35"/><stop offset="1" stop-color="{CRIMSON}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="ul" x1="0" x2="1"><stop offset="0" stop-color="{CRIMSON}"/><stop offset="1" stop-color="{CRIMSON}" stop-opacity="0"/></linearGradient>
  <clipPath id="c"><rect width="{w}" height="{h}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="url(#g)"/>
  <rect width="{w}" height="{h}" fill="url(#glow)"/>
  {slashes}
  <rect x="0" y="0" width="6" height="{h}" fill="{CRIMSON}"/>
  <rect x="0" y="{h-3}" width="{w}" height="3" fill="url(#ul)"/>
</g>
<g class="a1">
  <text x="70" y="78" class="m" font-size="14" font-weight="700" fill="{CRIMSON}" letter-spacing="4">PORTAFOLIO · GITHUB</text>
</g>
<g class="a2">
  <text x="66" y="162" class="b" font-size="88" fill="{BONE}" letter-spacing="2">{escape(name)}</text>
  <rect x="70" y="182" width="180" height="4" fill="url(#ul)"/>
  <text x="70" y="220" class="m" font-size="19" fill="{TEXT}">Ingeniería de Sistemas — Universidad El Bosque</text>
</g>
<g class="a3">
  <text x="70" y="256" class="m" font-size="14" font-weight="700" fill="{CRIMSON_LIGHT}" letter-spacing="1.5">BACKEND  ·  FULL-STACK  ·  SEGURIDAD DE LA INFORMACIÓN  ·  SISTEMAS EMBEBIDOS</text>
  <rect x="70" y="276" width="262" height="30" rx="15" fill="#1A0708" stroke="{BLOOD}"/>
  <circle class="dot" cx="92" cy="291" r="5" fill="{CRIMSON_LIGHT}"/>
  <text x="106" y="296" class="m" font-size="12.5" font-weight="700" fill="{BONE}" letter-spacing="1">DISPONIBLE PARA PRÁCTICA</text>
</g>"""
    return svg_doc(w, h, body, extra_css=css, title="Juan Sebastián Pineda Santafé — Ingeniería de Sistemas")


def section_svg(title):
    w, h = 880, 56
    tw = text_width(title, 34)
    body = f"""
<defs><linearGradient id="ul" x1="0" x2="1"><stop offset="0" stop-color="{CRIMSON}"/><stop offset="1" stop-color="{CRIMSON}" stop-opacity="0"/></linearGradient></defs>
<rect x="0" y="0" width="{w}" height="{h}" rx="10" fill="{BG}"/>
<rect x="0" y="0" width="5" height="{h}" rx="2" fill="{CRIMSON}"/>
<text x="24" y="40" class="b" font-size="34" fill="{BONE}">{escape(title)}</text>
<rect x="{24 + tw + 16:.0f}" y="28" width="{w - (24 + tw + 16) - 24:.0f}" height="1.5" fill="url(#ul)"/>"""
    return svg_doc(w, h, body, fonts=("bebas",), title=title)


def wrap(text, max_chars):
    lines, line = [], ""
    for word in text.split():
        if len(line) + len(word) + (1 if line else 0) > max_chars:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    return lines + ([line] if line else [])


def project_svg(category, title, desc, tags):
    w, h = 430, 250
    fs = 12.5
    max_chars = int((w - 56) / (fs * 0.6))
    body = card_frame(w, h)
    body += f'<clipPath id="cc"><rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="10"/></clipPath>'
    body += f'<rect x="0" y="0" width="4" height="{h}" fill="{CRIMSON}" clip-path="url(#cc)"/>'
    body += (f'<text x="28" y="38" class="m" font-size="11" font-weight="700" fill="{CRIMSON_LIGHT}" '
             f'letter-spacing="1.5">{escape(category.upper())}</text>')
    body += (f'<text x="{w-24}" y="38" class="m" font-size="10.5" fill="{MUTED}" '
             f'text-anchor="end">VER REPOSITORIO →</text>')
    body += f'<text x="28" y="80" class="b" font-size="36" fill="{BONE}">{escape(title)}</text>'
    body += f'<rect x="28" y="92" width="90" height="2" fill="url(#ln)"/>'
    for i, line in enumerate(wrap(desc, max_chars)[:5]):
        body += f'<text x="28" y="{120 + i*19}" class="m" font-size="{fs}" fill="{TEXT}">{escape(line)}</text>'
    x, y = 28, h - 38
    for t in tags:
        tw = len(t) * 6.6 + 20
        if x + tw > w - 24:
            break
        body += f'<rect x="{x}" y="{y}" width="{tw:.0f}" height="22" rx="11" fill="#1A0A0B" stroke="#5C0000"/>'
        body += (f'<text x="{x + tw/2:.0f}" y="{y+15}" class="m" font-size="11" fill="#D4C5B0" '
                 f'text-anchor="middle">{escape(t)}</text>')
        x += tw + 8
    return svg_doc(w, h, body, title=f"{title}: {desc}")


PROJECTS = {
    "project-honeycomb.svg": (
        "Motor de juego · NoCode", "HONEYCOMB ENGINE",
        "Plataforma NoCode para crear niveles isométricos 2.5D. Editor de escritorio con drag & drop y "
        "motor nativo en C++17 + raylib con Z-sorting y colisiones, comunicados por un contrato JSON.",
        ["C++17", "raylib", "Angular", "Electron", "CMake"]),
    "project-tienda.svg": (
        "Full-stack · Backend", "TIENDA DS",
        "Sistema de gestión comercial con API REST en ASP.NET Core 8 por capas, bases de datos separadas "
        "por dominio, autenticación JWT + BCrypt, Docker Compose y CI/CD con GitHub Actions.",
        ["C#", "EF Core", "MySQL", "Angular", "Docker"]),
    "project-cifrado.svg": (
        "Seguridad · Cloud", "CIFRADO Y AUTENTICACIÓN",
        "Criptoanálisis automático de César, Afín y Vigenère. Login con bcrypt, sesiones y protección "
        "contra fuerza bruta, desplegado en AWS EC2 con nginx y certificados TLS de Let's Encrypt.",
        ["TypeScript", "Angular SSR", "Express", "AWS", "nginx"]),
    "project-dsl.svg": (
        "Lenguajes · Reglas de negocio", "CREDITRULES DSL",
        "Lenguaje de dominio específico para evaluar solicitudes de crédito. Las reglas se modelan como "
        "un AST con evaluación interactiva, casos de prueba y exportación de los árboles a Graphviz.",
        ["C#", ".NET", "AST", "Graphviz"]),
}

SECTIONS = {
    "section-about.svg": "SOBRE MÍ",
    "section-projects.svg": "PROYECTOS DESTACADOS",
    "section-others.svg": "OTROS PROYECTOS",
    "section-metrics.svg": "MÉTRICAS DE GITHUB",
    "section-stack.svg": "TECNOLOGÍAS",
    "section-education.svg": "FORMACIÓN",
    "section-contact.svg": "CONTACTO",
}


def build_static():
    print("Generando recursos estáticos…")
    write("header.svg", header_svg())
    for file, title in SECTIONS.items():
        write(file, section_svg(title))
    for file, args in PROJECTS.items():
        write(file, project_svg(*args))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "metrics"
    if cmd in ("static", "all"):
        build_static()
    if cmd in ("metrics", "all"):
        build_metrics()
