import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[2]

class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids = [], set()
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])

class SiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / '_build', self.root / '_build')
        spec = importlib.util.spec_from_file_location('site_builder', self.root / '_build/build.py')
        self.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.builder)
    def fixture(self, entries):
        (self.root / '_build/letters.json').write_text(json.dumps(entries))
        folder = self.root / '_build/letters'
        folder.mkdir(exist_ok=True)
        for entry in entries:
            (folder / (entry['slug'] + '.md')).write_text('A concrete **argument**, with a qualification.')
    def letter(self, **changes):
        return dict(slug='test-letter', title='A question & an objection', description='A test description', date='2026-11-17', status='published', sources='[Source](https://example.org/source)', **changes)
    def test_article_archive_and_sitemap(self):
        item = self.letter()
        draft = dict(item, slug='unpublished', status='draft')
        self.fixture([item, draft])
        self.builder.build_letters()
        self.builder.build_meta()
        article = (self.root / 'letters/test-letter/index.html').read_text()
        self.assertIn('By Alex Omberg', article)
        self.assertIn('https://example.org/source', article)
        self.assertIn('https://alexomberg.com/letters/test-letter/', article)
        import re
        data = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', article, re.S)]
        self.assertTrue(any(x.get('@type') == 'Article' and x['datePublished'] == item['date'] for x in data))
        self.assertIn('/letters/test-letter/', (self.root / 'letters/index.html').read_text())
        self.assertIn('/letters/test-letter/', (self.root / 'sitemap.xml').read_text())
        self.assertFalse((self.root / 'letters/unpublished/index.html').exists())
        self.assertNotIn('/letters/unpublished/', (self.root / 'sitemap.xml').read_text())
        self.fixture([dict(item, status='draft')])
        with self.assertRaisesRegex(ValueError, 'Previously generated'):
            self.builder.build_letters()
    def test_duplicate_slug_rejected(self):
        self.fixture([self.letter(), self.letter()])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.builder.published_letters()
    def test_public_internal_links_and_anchors(self):
        for path in ROOT.rglob('*.html'):
            if '_build' in path.parts:
                continue
            for link in Links(path.read_text()).links:
                url = urlsplit(link)
                if url.scheme or url.netloc:
                    continue
                target = (ROOT / url.path.lstrip('/')) if url.path.startswith('/') else (path.parent / url.path)
                if not url.path:
                    target = path
                if target.is_dir():
                    target /= 'index.html'
                with self.subTest(page=str(path.relative_to(ROOT)), link=link):
                    self.assertTrue(target.exists())
                    if url.fragment and target.suffix == '.html':
                        self.assertIn(unquote(url.fragment), Links(target.read_text()).ids)

if __name__ == '__main__':
    unittest.main()
