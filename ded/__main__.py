"""
ded: deadfiles, in python
  Try to find all unused files in a source tree.
Builds an ~adjacency matrix <file, [import]>
Then a set of dependencies {filename}
Then a set of source {filenames}
And with some js lib rules:
  - no '^@.*'
  - no <name> in <libs>
  not in dep => ded
Enjoy the difference.
"""

import os
import re
import json
from pathlib import Path
from typing import Generator, List


ROOT = "./src"

LIBS = []

def allfiles(root):
    """
    List all files under root.
    """
    for top, _, files in os.walk(root):
        _ = Path(top)
        yield from (_ / f for f in files)


def index(paths: List[str]) -> List[str]:
    """
    Create an index.
    """
    print(paths)
    return []


def imports(filename: str) -> Generator[str, None, None]:
    """
    read filename, find all imports
    """
    with open(filename, "r", encoding="utf8") as src:
        for line in src.readlines():
            if "import" in line:
                yield line.strip()


RE = ".*from *(?P<src>.*)"


def parse_import(definition):
    """
    'import ... from ...' -> Import(...) {'src': <reference>}
    """
    m = re.match(RE, definition)
    if m:
        g = m.groupdict()
        if g:
            return True, g["src"]
    return False, definition


def test():
    """
    Test.
    """

    def maybeGroupDict(m):
        return m.groupdict() if m else m

    def part(seq, p):
        t = []
        f = []
        ta = t.append
        fa = f.append
        for e in seq:
            (ta if p(e) else fa)(e)
        return t, f

    base = list(allfiles(ROOT))
    idx = {f: [parse_import(l) for l in imports(f.absolute())] for f in base}
    allimports = [line for seq in idx.values() for line in seq]
    _ = [(imp, maybeGroupDict(re.match(RE, imp))) for imp in allimports]
    return _


class ImportsResolver:

    def libs(self, root):
        pass

    def imports(self, path):
        pass

    def in_libs(self, dep, libs):
        pass

class JavascriptResolver(ImportsResolver):

    def libs(package_json='package.json'):
        with open(package_json, 'r') as src:
            j = json.load(src)
            return  list(j['dependencies'].keys())

    def imports(path):
        return [parse_import(l) for l in imports(path.absolute())]

    def in_libs(dep, libs):
        return any(dep.startswith(lib) for lib in libs)



def main(resolver):
    """
    Build matrices and sets.
    """
    base = list(allfiles(ROOT))
    idx = {f.relative_to(ROOT): resolver.imports(f) for f in base}
    sdep = set(re.sub("[';]", "", dep) for fn, deps in idx.items() for (ok, dep) in deps if ok)
    slibs = set(libs())
    sldep = set(dep for dep in sdep if not dep_in_libs(dep, slibs))  # local dep not in libs

if __name__ == "__main__":
    main()
