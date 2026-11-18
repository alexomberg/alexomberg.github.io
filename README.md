# alexomberg.com

Static site for Alex Omberg, served by GitHub Pages at https://alexomberg.com.

- Content and templates live in `_build/` (`books.json`, `config.json`, `about.md`, `privacy.md`, `build.py`).
- Rebuild: `python3 _build/build.py` (needs the `markdown` package). Icons and the share card: `python3 _build/gen_images.py`.
- Visual system: the Alex Omberg Design System (paper `#FFFFFA`, ink `#181716`, orange `#FF3700`, Literata headings, Inter body/UI, abstract owl). Fonts are self-hosted; the site loads no third-party scripts, cookies or analytics.
- Newsletter form posts directly to Kit form 8419424.

## Reading guide and letters

Edit `_build/start-here.md` for the reading guide. It links to existing catalog anchors; review book scope, edition and author credit against the Publishing Database before adding or changing purchase destinations.

To add an approved letter, create `_build/letters/<slug>.md` and add an entry to `_build/letters.json`:

```json
{
  "slug": "a-question-worth-considering",
  "title": "A question worth considering",
  "description": "A short, accurate description of this letter.",
  "date": "2026-11-17",
  "status": "published",
  "sources": "A short Markdown source note with links to the works discussed."
}
```

Rebuild and commit both the source and generated files. The build creates the article, archive entry, canonical URL, Article metadata and sitemap entry. Dates are editorial publication dates, not a scheduling mechanism: `published` renders immediately, even with a future date. Other statuses are omitted from generated listings. Changing a previously published slug/status requires explicitly reviewing and removing its old generated page; the builder stops if it detects stale article pages.

This is a public repository, and `.nojekyll` means build-source files may also be served by Pages. Keep private or unapproved drafts outside this repository. A draft status is not access control.

The archive intentionally starts empty. Add the first approved letter before launching the content pilot. The existing Kit destination is preserved; successful signup, confirmation and delivery still require an end-to-end test.

Preview locally with `python3 -m http.server 8765 --bind 127.0.0.1`. Run `python3 -m unittest discover -s _build/tests` to validate letter generation and internal links. Publish only through the existing approved deployment process; building locally does not publish.

The self-hosted Inter WOFF2 subset covers Latin and Latin Extended characters plus common punctuation and symbols. Inter is distributed under its bundled `assets/fonts/Inter-OFL.txt` license. Literata's existing license remains in `assets/fonts/`.
