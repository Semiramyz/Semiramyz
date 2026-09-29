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

# ─── Paleta (tonos papel, grises cálidos y pasteles) ───────────────────────
PAPER = "#EFEBE0"
LINE = "#D2CBBA"
INK = "#4A4740"
TEXT = "#6E6A5F"
MUTED = "#9C968A"
SAGE, SAGE_D = "#A8B5A2", "#6F8069"
LAVENDER, LAVENDER_D = "#B7AFCF", "#7A7196"
ROSE, ROSE_D = "#D4A5A5", "#9A6666"
SKY, SKY_D = "#A9C1CF", "#62808F"
SAND = "#D8C9A7"
LANG_COLORS = ["#A8B5A2", "#B7AFCF", "#D4A5A5", "#A9C1CF", "#D8C9A7", "#C4B5A5", "#9FBFB8", "#BDB6A8"]
HEAT = ["#E2DDCF", "#CFD6C8", "#B2C0AC", "#8FA38A", "#6C8067"]
BULLETS = [SAGE, LAVENDER, ROSE, SKY]
DAYS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MONTHS_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


# ─── Utilidades SVG ────────────────────────────────────────────────────────
def font_css(*names):
    faces = {
        "serif": ("Serif", "CormorantGaramond-SemiBold.woff2", 600),
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
    css.append(".b{font-family:'Serif','Georgia','Times New Roman',serif;font-weight:600}")
    css.append(".m{font-family:'Mono','Consolas','Courier New',monospace}")
    return "".join(css)


def svg_doc(w, h, body, fonts=("serif", "mono", "monob"), extra_css="", title=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>'
        f"<style>{font_css(*fonts)}{extra_css}</style>{body}</svg>"
    )


def card_frame(w, h):
    return (
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12" fill="{PAPER}" stroke="{LINE}"/>'
        f'<rect x="6.5" y="6.5" width="{w-13}" height="{h-13}" rx="8" fill="none" stroke="{LINE}" stroke-opacity=".55"/>'
    )


def card_title(w, title, right=""):
    s = f'<rect x="24" y="30" width="8" height="8" fill="{INK}" opacity=".7" transform="rotate(45 28 34)"/>'
    s += f'<text x="42" y="41" class="b" font-size="25" fill="{INK}" letter-spacing=".5">{escape(title)}</text>'
    if right:
        s += f'<text x="{w-24}" y="39" class="m" font-size="11" fill="{MUTED}" text-anchor="end">{escape(right)}</text>'
    s += f'<rect x="24" y="53" width="{w-48}" height="1" fill="{LINE}"/>'
    s += f'<rect x="24" y="52" width="46" height="3" fill="{SAGE}"/>'
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
        body += f'<circle cx="{x0+3}" cy="{y-4}" r="3.5" fill="{BULLETS[i % 4]}"/>'
        body += f'<text x="{x0+14}" y="{y}" class="m" font-size="12.5" fill="{TEXT}">{escape(label)}</text>'
        body += (f'<text x="{x0+176}" y="{y}" class="m" font-size="14" font-weight="700" '
                 f'fill="{INK}" text-anchor="end">{escape(value)}</text>')
    return svg_doc(w, h, body, title="Resumen de actividad en GitHub")


def languages_card(d):
    w, h = 420, 214
    total = sum(d["langs"].values()) or 1
    top = d["langs"].most_common()
    if len(top) > 8:
        top = top[:7] + [("Otros", sum(s for _, s in top[7:]))]
    body = card_frame(w, h) + card_title(w, "Lenguajes más usados", "por código")
    body += '<defs><clipPath id="bar"><rect x="24" y="70" width="372" height="10" rx="5"/></clipPath></defs>'
    body += f'<g clip-path="url(#bar)"><rect x="24" y="70" width="372" height="10" fill="{LINE}"/>'
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
        body += f'<text x="{x0+16}" y="{y}" class="m" font-size="12.5" fill="{INK}">{escape(lang[:14])}</text>'
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
    body += (f'<defs><linearGradient id="bg1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{LAVENDER}"/>'
             f'<stop offset="1" stop-color="{SKY}" stop-opacity="0.7"/></linearGradient>'
             f'<linearGradient id="bg2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ROSE}"/>'
             f'<stop offset="1" stop-color="{SAND}"/></linearGradient></defs>')
    left, right, base, top = 60, w - 36, 176, 78
    slot = (right - left) / 24
    mx = max(hours) or 1
    peak = hours.index(max(hours)) if total else -1
    for frac in (0.5, 1.0):
        gy = base - (base - top) * frac
        body += f'<line x1="{left}" y1="{gy}" x2="{right}" y2="{gy}" stroke="{LINE}" stroke-dasharray="3 5"/>'
    body += f'<line x1="{left}" y1="{base}" x2="{right}" y2="{base}" stroke="{LINE}"/>'
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
                     f'fill="{INK}" text-anchor="middle">{n}</text>')
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
def text_width(text, size, file="CormorantGaramond-SemiBold.woff2", letter_spacing=1.0):
    from fontTools.ttLib import TTFont  # solo se necesita para los recursos estáticos
    f = TTFont(FONTS / file)
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    units = sum(hmtx[cmap[ord(ch)]][0] for ch in text if ord(ch) in cmap)
    return units * size / upm + letter_spacing * len(text)


def header_svg():
    w, h = 1200, 330
    name = "Juan Sebastián Pineda Santafé"
    grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="{LINE}" stroke-opacity=".35"/>' for x in range(40, w, 40))
    grid += "".join(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="{LINE}" stroke-opacity=".35"/>' for y in range(40, h, 40))
    css = (
        "@keyframes f{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"
        ".a1{animation:f 1.2s ease-out both}.a2{animation:f 1.2s .3s ease-out both}.a3{animation:f 1.2s .6s ease-out both}"
        "@keyframes p{0%,100%{opacity:1}50%{opacity:.3}}.dot{animation:p 3s ease-in-out infinite}"
        "@keyframes d{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}.fl{animation:d 7s ease-in-out infinite}"
    )
    body = f"""
<defs>
  <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#F4F1E9"/><stop offset="1" stop-color="#E6E0D1"/>
  </linearGradient>
  <radialGradient id="r1"><stop offset="0" stop-color="{LAVENDER}" stop-opacity=".55"/><stop offset="1" stop-color="{LAVENDER}" stop-opacity="0"/></radialGradient>
  <radialGradient id="r2"><stop offset="0" stop-color="{SAGE}" stop-opacity=".55"/><stop offset="1" stop-color="{SAGE}" stop-opacity="0"/></radialGradient>
  <radialGradient id="r3"><stop offset="0" stop-color="{ROSE}" stop-opacity=".45"/><stop offset="1" stop-color="{ROSE}" stop-opacity="0"/></radialGradient>
  <clipPath id="c"><rect width="{w}" height="{h}" rx="16"/></clipPath>
</defs>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="url(#g)"/>
  {grid}
  <circle cx="1010" cy="95" r="190" fill="url(#r1)"/>
  <circle cx="1120" cy="270" r="170" fill="url(#r2)"/>
  <circle cx="870" cy="300" r="140" fill="url(#r3)"/>
  <g class="fl" fill="none" stroke="{INK}" stroke-opacity=".35">
    <rect x="1045" y="120" width="70" height="70" transform="rotate(45 1080 155)"/>
    <rect x="1063" y="138" width="34" height="34" transform="rotate(45 1080 155)"/>
    <line x1="990" y1="155" x2="1030" y2="155"/><line x1="1130" y1="155" x2="1170" y2="155"/>
  </g>
  <rect x="0" y="0" width="{w}" height="{h}" rx="16" fill="none" stroke="{LINE}" stroke-width="2"/>
  <rect x="12" y="12" width="{w-24}" height="{h-24}" rx="10" fill="none" stroke="{LINE}"/>
</g>
<g class="a1">
  <text x="70" y="82" class="m" font-size="13" font-weight="700" fill="{MUTED}" letter-spacing="4">PORTAFOLIO · GITHUB</text>
</g>
<g class="a2">
  <text x="66" y="158" class="b" font-size="66" fill="{INK}">{escape(name)}</text>
  <rect x="70" y="180" width="520" height="1" fill="{LINE}"/>
  <rect x="70" y="179" width="70" height="3" fill="{SAGE}"/>
  <text x="70" y="216" class="m" font-size="18" fill="{TEXT}">Ingeniería de Sistemas — Universidad El Bosque</text>
</g>
<g class="a3">
  <text x="70" y="252" class="m" font-size="13" font-weight="700" fill="{SAGE_D}" letter-spacing="1.5">BACKEND  ·  FULL-STACK  ·  SEGURIDAD DE LA INFORMACIÓN  ·  SISTEMAS EMBEBIDOS</text>
  <rect x="70" y="272" width="262" height="30" rx="15" fill="#E3E8DF" stroke="{SAGE}"/>
  <circle class="dot" cx="92" cy="287" r="5" fill="{SAGE_D}"/>
  <text x="106" y="292" class="m" font-size="12.5" font-weight="700" fill="{INK}" letter-spacing="1">DISPONIBLE PARA PRÁCTICA</text>
</g>"""
    return svg_doc(w, h, body, extra_css=css, title="Juan Sebastián Pineda Santafé — Ingeniería de Sistemas")


def section_svg(title):
    w, h = 880, 56
    tw = text_width(title, 28, file="CormorantGaramond-SemiBold.woff2", letter_spacing=3)
    x1 = 44 + tw + 18
    body = f"""
<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="10" fill="{PAPER}" stroke="{LINE}"/>
<rect x="22" y="24" width="9" height="9" fill="{INK}" opacity=".7" transform="rotate(45 26.5 28.5)"/>
<text x="44" y="38" class="b" font-size="28" fill="{INK}" letter-spacing="3">{escape(title)}</text>
<rect x="{x1:.0f}" y="28" width="{w - x1 - 44:.0f}" height="1" fill="{LINE}"/>
<rect x="{w-36}" y="24.5" width="7" height="7" fill="none" stroke="{MUTED}" transform="rotate(45 {w-32.5} 28)"/>"""
    return svg_doc(w, h, body, fonts=("serif",), title=title)


def wrap(text, max_chars):
    lines, line = [], ""
    for word in text.split():
        if len(line) + len(word) + (1 if line else 0) > max_chars:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    return lines + ([line] if line else [])


def project_svg(category, title, desc, tags, accent=(SAGE, SAGE_D)):
    light, dark = accent
    w, h = 430, 250
    fs = 12.5
    max_chars = int((w - 56) / (fs * 0.6))
    body = card_frame(w, h)
    body += f'<rect x="7" y="7" width="4" height="{h-14}" rx="2" fill="{light}"/>'
    body += (f'<text x="28" y="40" class="m" font-size="11" font-weight="700" fill="{dark}" '
             f'letter-spacing="1.5">{escape(category.upper())}</text>')
    body += (f'<text x="{w-24}" y="40" class="m" font-size="10.5" fill="{MUTED}" '
             f'text-anchor="end">VER REPOSITORIO →</text>')
    body += f'<text x="28" y="80" class="b" font-size="31" fill="{INK}">{escape(title)}</text>'
    body += f'<rect x="28" y="92" width="{w-56}" height="1" fill="{LINE}"/>'
    body += f'<rect x="28" y="91" width="46" height="3" fill="{light}"/>'
    for i, line in enumerate(wrap(desc, max_chars)[:5]):
        body += f'<text x="28" y="{120 + i*19}" class="m" font-size="{fs}" fill="{TEXT}">{escape(line)}</text>'
    x, y = 28, h - 40
    for t in tags:
        tw = len(t) * 6.6 + 20
        if x + tw > w - 24:
            break
        body += (f'<rect x="{x}" y="{y}" width="{tw:.0f}" height="22" rx="11" fill="{light}" '
                 f'fill-opacity=".3" stroke="{light}"/>')
        body += (f'<text x="{x + tw/2:.0f}" y="{y+15}" class="m" font-size="11" fill="{INK}" '
                 f'text-anchor="middle">{escape(t)}</text>')
        x += tw + 8
    return svg_doc(w, h, body, title=f"{title}: {desc}")


PROJECTS = {
    "project-honeycomb.svg": (
        "Motor de juego · NoCode", "HoneyComb Engine",
        "Plataforma NoCode para crear niveles isométricos 2.5D. Editor de escritorio con drag & drop y "
        "motor nativo en C++17 + raylib con Z-sorting y colisiones, comunicados por un contrato JSON.",
        ["C++17", "raylib", "Angular", "Electron", "CMake"], (SAND, "#8A7A55")),
    "project-tienda.svg": (
        "Full-stack · Backend", "Tienda DS",
        "Sistema de gestión comercial con API REST en ASP.NET Core 8 por capas, bases de datos separadas "
        "por dominio, autenticación JWT + BCrypt, Docker Compose y CI/CD con GitHub Actions.",
        ["C#", "EF Core", "MySQL", "Angular", "Docker"], (SKY, SKY_D)),
    "project-cifrado.svg": (
        "Seguridad · Cloud", "Cifrado y Autenticación",
        "Criptoanálisis automático de César, Afín y Vigenère. Login con bcrypt, sesiones y protección "
        "contra fuerza bruta, desplegado en AWS EC2 con nginx y certificados TLS de Let's Encrypt.",
        ["TypeScript", "Angular SSR", "Express", "AWS", "nginx"], (LAVENDER, LAVENDER_D)),
    "project-dsl.svg": (
        "Lenguajes · Reglas de negocio", "CreditRules DSL",
        "Lenguaje de dominio específico para evaluar solicitudes de crédito. Las reglas se modelan como "
        "un AST con evaluación interactiva, casos de prueba y exportación de los árboles a Graphviz.",
        ["C#", ".NET", "AST", "Graphviz"], (ROSE, ROSE_D)),
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
