"""French edition of a country site (config "lang2": "fr").

The generator keeps its two internal language slots ("ar" and "en"); for a country with lang2 == "fr" the English slot is
rewritten to French at load time (fr_pairs.txt: exact source fragments -> French) and the finished site is published under /fr/.
Nothing in build.py / content.py / templates has to be duplicated."""
import importlib.abc
import importlib.machinery
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def lang2_of(country):
    try:
        cfg = json.loads((ROOT / country / "config.json").read_text(encoding="utf-8"))
        return cfg.get("lang2")
    except Exception:
        return None


def _pairs_file():
    c = os.environ.get("COUNTRY", "").strip()
    return "sa_pairs.txt" if lang2_of(c) == "para" else "fr_pairs.txt"


def load_pairs():
    txt = (ROOT / _pairs_file()).read_text(encoding="utf-8")
    pairs = []
    for m in re.finditer(r"<<<\n(.*?)\n===\n(.*?)\n>>>", txt, re.S):
        pairs.append((m.group(1), m.group(2)))
    pairs.sort(key=lambda p: -len(p[0]))  # longest first so a short fragment never cuts into a longer one
    return pairs


PAIRS = load_pairs()
HITS = {}


def tr(text):
    for i, (a, b) in enumerate(PAIRS):
        if a in text:
            text = text.replace(a, b)
            HITS[i] = HITS.get(i, 0) + 1
    return text


class _Loader(importlib.abc.SourceLoader):
    def __init__(self, path):
        self.path = str(path)

    def get_filename(self, fullname):
        return self.path

    def get_data(self, path):
        return tr(Path(path).read_text(encoding="utf-8")).encode("utf-8")


class _Finder(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name == "content":
            return importlib.util.spec_from_loader(name, _Loader(ROOT / "content.py"))
        if name == "content_guides":  # the long buying guides are Saudi-market prose written for ar/en only
            return importlib.util.spec_from_loader(name, _StubLoader())
        return None


class _StubLoader(importlib.abc.Loader):
    def create_module(self, spec):
        return None

    def exec_module(self, module):
        module.GUIDES = {}


def run(build_file, country):
    import importlib.util
    importlib.util.spec_from_loader  # noqa: B018 (makes sure the submodule is loaded)
    sys.meta_path.insert(0, _Finder())
    from jinja2 import FileSystemLoader
    orig = FileSystemLoader.get_source

    def get_source(self, environment, template):
        src, filename, uptodate = orig(self, environment, template)
        return tr(src), filename, uptodate

    FileSystemLoader.get_source = get_source
    code = tr(Path(build_file).read_text(encoding="utf-8"))
    g = {"__name__": "__main__", "__file__": str(build_file), "_FR_DONE": True}
    exec(compile(code, str(build_file), "exec"), g)
    finish(country)


def finish(country):
    """dist/<country>/en -> dist/<country>/fr and every link/hreflang with it."""
    out = ROOT / "dist" / country
    if lang2_of(country) != "fr":  # source-text rewrite only (no French edition)
        miss = [PAIRS[i][0][:70] for i in range(len(PAIRS)) if i not in HITS]
        if miss:
            print(f"fr_patch: {len(miss)} fragments did not match:", *miss, sep="\n  ")
        return
    if (out / "en").exists():
        (out / "en").rename(out / "fr")
    pairs = [(f"/{country}/en/", f"/{country}/fr/"), ('hreflang="en"', 'hreflang="fr"'), ('<html lang="en"', '<html lang="fr"'),
             ('content="en_US"', 'content="fr_FR"'), ('hreflang="en-TN"', 'hreflang="fr-TN"'), (' lang="en">', ' lang="fr">')]
    for f in out.rglob("*"):
        if f.is_file() and f.suffix in (".html", ".xml", ".json", ".txt"):
            t = f.read_text(encoding="utf-8")
            n = t
            for a, b in pairs:
                n = n.replace(a, b)
            if f.suffix == ".html" or f.suffix == ".xml":
                n = re.sub(r'(["\'(=])/' + country + r'/en/', r'\1/' + country + "/fr/", n)
            if n != t:
                f.write_text(n, encoding="utf-8")
    miss = [PAIRS[i][0][:70] for i in range(len(PAIRS)) if i not in HITS]
    if miss:
        print(f"fr_patch: {len(miss)} fragments did not match:", *miss, sep="\n  ")
