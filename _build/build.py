#!/usr/bin/env python3
"""Builds alexomberg.com into the repository root from books.json, privacy.md and the templates below.

Run from anywhere:  python3 _build/build.py
Plain static output, no runtime dependencies; GitHub Pages serves it as-is (.nojekyll).
"""
import html, json, pathlib, re
from datetime import date
import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD = ROOT / "_build"
SITE_URL = "https://alexomberg.com"
EMAIL = "alex@alexomberg.com"
KIT_FORM = "https://app.kit.com/forms/8419424/subscriptions"

CONFIG = json.loads((BUILD / "config.json").read_text())
BOOKS = json.loads((BUILD / "books.json").read_text())
e = html.escape

NAV = [("Books", "/books/"), ("About", "/about/"), ("Contact", "/contact/")]
FOOT_NAV = NAV + [("Privacy", "/privacy/")]


def person_ld():
    same = [p["url"] for p in CONFIG.get("profiles", []) if p.get("url")]
    d = {"@context": "https://schema.org", "@type": "Person", "@id": SITE_URL + "/#author",
         "name": "Alex Omberg", "url": SITE_URL + "/", "email": "mailto:" + EMAIL,
         "description": CONFIG["description"], "knowsAbout": ["Philosophy", "History of philosophy", "Western philosophy"]}
    if same:
        d["sameAs"] = same
    return d


def page(path, title, description, body, current=None, extra_ld=None, robots=None):
    full_title = "Alex Omberg" if title is None else f"{title} · Alex Omberg"
    url = SITE_URL + path
    lds = [person_ld()] + (extra_ld or [])
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    nav = "".join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a></li>' for label, href in NAV)
    fnav = "".join(f'<li><a href="{href}">{label}</a></li>' for label, href in FOOT_NAV)
    me_links = "".join(f'\n<link rel="me" href="{e(p["url"])}">' for p in CONFIG.get("profiles", []) if p.get("url"))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
<meta name="author" content="Alex Omberg">
{f'<meta name="robots" content="{robots}">' if robots else ''}
<link rel="canonical" href="{url}">{me_links}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Alex Omberg">
<meta property="og:title" content="{e(title or 'Alex Omberg')}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}/assets/img/og-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Alex Omberg owl mark and wordmark on warm paper">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title or 'Alex Omberg')}">
<meta name="twitter:description" content="{e(description)}">
<meta name="twitter:image" content="{SITE_URL}/assets/img/og-card.png">
<meta name="theme-color" content="#FFFFFA">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/Literata-VF.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
{ld}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<div class="wrap">
<header class="ao-header">
 <a class="ao-lockup" href="/" aria-label="Alex Omberg, home"><img src="/assets/img/owl-ink.svg" alt="" width="14" height="28"><span class="ao-wordmark">Alex Omberg</span></a>
 <nav aria-label="Main"><ul class="ao-nav">{nav}</ul></nav>
</header>
</div>
<main id="main">
{body}
</main>
<footer class="ao-footer" data-theme="reversed">
 <div class="wrap">
  <div class="ao-footer__row">
   <a class="ao-lockup" href="/" aria-label="Alex Omberg, home"><img src="/assets/img/owl-paper.svg" alt="" width="14" height="28"><span class="ao-wordmark">Alex Omberg</span></a>
   <nav aria-label="Footer"><ul class="ao-nav">{fnav}</ul></nav>
  </div>
  <p class="ao-footer__fine">Alex Omberg · The Philosophy School · Western Philosophy Series<br>Contact: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
 </div>
</footer>
</body>
</html>
"""


def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def signup_form(fid):
    return f"""<form class="ao-signup" action="{KIT_FORM}" method="post" accept-charset="UTF-8">
 <div class="field-stack">
  <div>
   <label class="ao-signup__label" for="{fid}-name">First name <span class="muted">(optional)</span></label>
   <input class="ao-input" id="{fid}-name" name="fields[first_name]" type="text" autocomplete="given-name" style="width:100%">
  </div>
  <div>
   <label class="ao-signup__label" for="{fid}-email">Email address</label>
   <div class="ao-signup__row">
    <input class="ao-input" id="{fid}-email" name="email_address" type="email" autocomplete="email" required>
    <button class="ao-button" type="submit">Subscribe</button>
   </div>
  </div>
 </div>
 <p class="ao-signup__hint">Unsubscribe at any time. <a href="/privacy/">Privacy policy</a>.</p>
</form>"""


def store_links(b):
    out = []
    for s in b.get("links", []):
        out.append(f'<li><a class="ao-link" href="{e(s["url"])}" rel="noopener">{e(s["label"])}</a></li>')
    return f'<ul class="ao-book__links" aria-label="Where to find {e(b["title"])}">{"".join(out)}</ul>' if out else ""


def cover_html(b, cls="ao-book__cover", w=120):
    if b.get("cover"):
        h = round(w * b.get("cover_h", 180) / 120)
        return f'<img class="{cls}" src="{e(b["cover"])}" alt="Cover of {e(b["title"])}" width="{w}" height="{h}" loading="lazy" decoding="async">'
    return f'<span class="{cls} ao-book__cover--empty" aria-hidden="true"><span>{e(b["title"])}</span></span>'


def book_entry(b, n):
    sub = f'<p class="ao-book__subtitle">{e(b["subtitle"])}</p>' if b.get("subtitle") else ""
    desc = f'<p class="ao-book__desc">{e(b["desc"])}</p>' if b.get("desc") else ""
    return f"""<li class="ao-book" id="{e(b['slug'])}">{cover_html(b)}<div>
 <h3 class="ao-book__title">{e(b['title'])}</h3>{sub}{desc}{store_links(b)}</div></li>"""


def series_groups():
    order = [s["name"] for s in CONFIG["series"]]
    groups = {}
    for b in BOOKS:
        groups.setdefault(b["series"], []).append(b)
    names = [n for n in order if n in groups] + sorted(n for n in groups if n not in order)
    return [(n, sorted(groups[n], key=lambda x: x.get("order", 999))) for n in names]


def series_blurb(name):
    for s in CONFIG["series"]:
        if s["name"] == name:
            return s.get("blurb", "")
    return ""


# ---------------------------------------------------------------- pages

def build_home():
    feat = [b for b in BOOKS if b.get("featured")][:3] or BOOKS[:3]
    items = "".join(
        f"""<li>{cover_html(b, "featured__cover", 160)}<span class="ao-label ao-label--secondary">{e(b['series'])}</span>
<h3>{e(b['title'])}</h3>
<a class="ao-link" href="/books/#{e(b['slug'])}">More on this volume</a></li>""" for b in feat)
    featured = f"""<section class="section" aria-labelledby="h-books">
 <div class="wrap">
  <div class="section-head">
   <div class="stack-tight"><p class="ao-label"><span class="ao-marker" aria-hidden="true"></span>From the catalogue</p>
   <h2 class="title-2" id="h-books">Thinkers, movements and questions</h2></div>
   <a class="ao-link" href="/books/">All books</a>
  </div>
  <ul class="featured">{items}</ul>
 </div>
</section>""" if feat else ""

    body = f"""<div class="wrap">
 <section class="hero" aria-labelledby="h-hero">
  <div>
   <p class="ao-label"><span class="ao-marker" aria-hidden="true"></span>Western Philosophy Series</p>
   <h1 class="display" id="h-hero" style="margin-top:var(--space-5)">The great questions, and the minds that asked them.</h1>
   <p class="lead" style="margin-top:var(--space-6)">{e(CONFIG['home_lead'])}</p>
   <div class="actions" style="margin-top:var(--space-7)">
    <a class="ao-button" href="/books/">Browse the books</a>
    <a class="ao-button ao-button--secondary" href="#newsletter">Get the newsletter</a>
   </div>
  </div>
  <div class="hero__owl"><img src="/assets/img/owl-ink.svg" alt="" width="150" height="294"></div>
 </section>
</div>
{featured}
<section class="section" id="newsletter" aria-labelledby="h-news">
 <div class="wrap signup-band">
  <div class="stack-tight">
   <span class="ao-rule" aria-hidden="true"></span>
   <h2 class="title-2" id="h-news" style="margin-top:var(--space-5)">Essays and new volumes, by email.</h2>
   <p style="margin:var(--space-4) 0 0;max-width:var(--measure);color:var(--text-secondary)">{e(CONFIG['newsletter_blurb'])}</p>
  </div>
  {signup_form('home')}
 </div>
</section>"""
    write("index.html", page("/", None, CONFIG["description"], body, current=None))


def build_books():
    groups = series_groups()
    n = 0
    blocks = []
    ld_items = []
    for name, books in groups:
        entries = []
        for b in books:
            n += 1
            entries.append(book_entry(b, n))
            item = {"@type": "Book", "name": b["title"], "author": {"@id": SITE_URL + "/#author"},
                    "url": f"{SITE_URL}/books/#{b['slug']}"}
            if b.get("subtitle"): item["alternativeHeadline"] = b["subtitle"]
            if b.get("isbn"): item["isbn"] = b["isbn"]
            item["isPartOf"] = {"@type": "BookSeries", "name": name}
            same = [s["url"] for s in b.get("links", [])]
            if same: item["sameAs"] = same
            ld_items.append({"@type": "ListItem", "position": n, "item": item})
        blurb = series_blurb(name)
        sid = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        blocks.append(f"""<section class="series" aria-labelledby="s-{sid}">
 <div class="series__head"><h2 class="title-2" id="s-{sid}">{e(name)}</h2>{f'<p>{e(blurb)}</p>' if blurb else ''}</div>
 <ul class="book-list">{''.join(entries)}</ul>
</section>""")
    if not blocks:
        blocks.append('<p class="lead muted">The catalogue is being added.</p>')
    toc = "".join(
        f'<li><a class="ao-link" href="#s-{re.sub(r"[^a-z0-9]+", "-", nm.lower()).strip("-")}">{e(nm)}</a> <span class="muted">{len(bk)}</span></li>' for nm, bk in groups)
    toc_html = f'<nav class="series-toc" aria-label="Series"><p class="ao-label ao-label--secondary">{n} volumes in {len(groups)} series</p><ul>{toc}</ul></nav>' if groups else ""
    body = f"""<div class="wrap">
 <div class="page-head stack-tight">
  <p class="ao-label"><span class="ao-marker" aria-hidden="true"></span>Books by Alex Omberg</p>
  <h1 class="title-1">Books</h1>
  <p class="lead">{e(CONFIG['books_lead'])}</p>
  {toc_html}
 </div>
 <div style="padding-bottom:var(--space-9)">{''.join(blocks)}</div>
</div>"""
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": "Books by Alex Omberg", "itemListElement": ld_items}] if ld_items else []
    write("books/index.html", page("/books/", "Books", CONFIG["books_description"], body, current="/books/", extra_ld=ld))


def build_about():
    body = f"""<div class="wrap">
 <div class="page-head stack-tight">
  <p class="ao-label"><span class="ao-marker" aria-hidden="true"></span>About</p>
  <h1 class="title-1">Philosophy for readers who want the whole argument.</h1>
 </div>
 <div class="ao-prose" style="padding-bottom:var(--space-9)">
{markdown.markdown((BUILD / 'about.md').read_text())}
 </div>
</div>"""
    write("about/index.html", page("/about/", "About", CONFIG["about_description"], body, current="/about/"))


def build_contact():
    prof = [p for p in CONFIG.get("profiles", []) if p.get("url")]
    rows = "".join(
        f'<li><span class="ao-label ao-label--secondary">{e(p["label"])}</span><a class="ao-link" href="{e(p["url"])}" rel="me noopener">{e(p["display"])}</a></li>' for p in prof)
    elsewhere = f"""<h2 class="title-2" style="margin:var(--space-8) 0 var(--space-5)">Elsewhere</h2>
<ul class="elsewhere">{rows}</ul>""" if rows else ""
    body = f"""<div class="wrap">
 <div class="page-head stack-tight">
  <p class="ao-label"><span class="ao-marker" aria-hidden="true"></span>Contact</p>
  <h1 class="title-1">Write to Alex Omberg</h1>
  <p class="lead">{e(CONFIG['contact_lead'])}</p>
 </div>
 <div style="padding-bottom:var(--space-9)">
  <span class="ao-rule" aria-hidden="true"></span>
  <p class="ao-label" style="margin-top:var(--space-5)">Email</p>
  <p style="margin:var(--space-2) 0 0"><a class="contact-email" href="mailto:{EMAIL}">{EMAIL}</a></p>
  {elsewhere}
 </div>
</div>"""
    write("contact/index.html", page("/contact/", "Contact", f"Contact Alex Omberg, author of the Western Philosophy Series: {EMAIL}.", body, current="/contact/"))


def build_privacy():
    md = (BUILD / "privacy.md").read_text()
    body = f"""<div class="wrap">
 <div class="ao-prose" style="padding:var(--space-9) 0">
{markdown.markdown(md)}
 </div>
</div>"""
    write("privacy/index.html", page("/privacy/", "Privacy Policy", "How Alex Omberg collects, uses and protects personal data from this site and the mailing list.", body, robots="noindex, nofollow"))


def build_404():
    body = """<div class="wrap">
 <div class="page-head stack-tight" style="padding-bottom:var(--space-10)">
  <p class="ao-label"><span class="ao-marker" aria-hidden="true"></span>Error 404</p>
  <h1 class="title-1">This page could not be found.</h1>
  <p class="lead">The address may have changed. The <a class="ao-link" href="/books/">books</a> and the <a class="ao-link" href="/">home page</a> are good places to start again.</p>
 </div>
</div>"""
    write("404.html", page("/404.html", "Page not found", "Page not found.", body, robots="noindex"))


def build_meta():
    pages = ["/", "/books/", "/about/", "/contact/"]
    today = date.today().isoformat()
    urls = "".join(f"<url><loc>{SITE_URL}{p}</loc><lastmod>{today}</lastmod></url>" for p in pages)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    write("CNAME", "alexomberg.com\n")
    write(".nojekyll", "")


if __name__ == "__main__":
    build_home(); build_books(); build_about(); build_contact(); build_privacy(); build_404(); build_meta()
    print(f"Built {len(BOOKS)} books into {ROOT}")
