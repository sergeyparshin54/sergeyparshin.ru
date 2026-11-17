import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.main_count = 0
        self.h1_count = 0
        self.links = []
        self.assets = []
        self.meta_names = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "main":
            self.main_count += 1
        if tag == "h1":
            self.h1_count += 1
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "link" and attrs.get("href"):
            self.assets.append(attrs["href"])
        if tag == "meta" and attrs.get("name"):
            self.meta_names.add(attrs["name"])


class SiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = SiteParser()
        cls.parser.feed(HTML)

    def test_landmarks_and_contacts(self):
        self.assertEqual(1, self.parser.main_count)
        self.assertEqual(1, self.parser.h1_count)
        self.assertEqual(11, len(self.parser.links))
        for link in self.parser.links:
            self.assertTrue(link.startswith(("https://", "mailto:", "tel:")), link)
        self.assertIn("Pause motion", HTML)
        self.assertIn("prefers-reduced-motion", HTML)

    def test_metadata_and_jsonld(self):
        self.assertIn('<link rel="canonical" href="https://sergeyparshin.ru/">', HTML)
        for name in ("description", "theme-color", "twitter:card"):
            self.assertIn(name, self.parser.meta_names)
        self.assertIn('property="og:title"', HTML)
        match = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', HTML, re.DOTALL)
        self.assertIsNotNone(match)
        person = json.loads(match.group(1))
        self.assertEqual("Sergey Parshin", person["name"])
        self.assertEqual("https://sergeyparshin.ru/", person["url"])
        self.assertEqual(9, len(person["sameAs"]))

    def test_local_assets_and_no_third_party_font_request(self):
        self.assertNotIn("fonts.googleapis.com", HTML)
        self.assertNotIn("fonts.gstatic.com", HTML)
        for relative in self.parser.assets:
            if relative.startswith(("https://", "favicon")):
                continue
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertNotIn("..", path.parts)
        for relative in ("assets/fonts/jetbrains-mono-latin.woff2", "assets/fonts/jetbrains-mono-cyrillic.woff2"):
            self.assertEqual(b"wOF2", (ROOT / relative).read_bytes()[:4])


class ContactConsistencyTest(unittest.TestCase):
    def test_js_and_noscript_contacts_are_identical(self):
        js = re.findall(r'\{k:"(\w+)"', HTML)
        noscript = re.findall(r'\./open (\w+)</a>', HTML)
        self.assertEqual(js, noscript)
        self.assertEqual(11, len(js))

    def test_share_image_is_large_and_local(self):
        self.assertIn('content="summary_large_image"', HTML)
        self.assertIn('property="og:image:width" content="1200"', HTML)
        self.assertIn('property="og:image:height" content="630"', HTML)
        image = ROOT / "assets/share.png"
        self.assertTrue(image.is_file())
        self.assertEqual(b"\x89PNG", image.read_bytes()[:4])
        self.assertIn('content="https://sergeyparshin.ru/assets/share.png"', HTML)


if __name__ == "__main__":
    unittest.main()
