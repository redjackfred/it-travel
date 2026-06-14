#!/usr/bin/env python3
"""Replace font links and stylesheet in handbook HTML files."""

import re
from pathlib import Path

ROOT = Path(__file__).parent
SNIPPET = (ROOT / "styles.css.snippet").read_text(encoding="utf-8")
FILES = [ROOT / "多洛米蒂旅遊手冊.html", ROOT / "index.html"]

PAT = re.compile(
    r'<link rel="preconnect" href="https://fonts\.googleapis\.com">.*?<style>.*?</style>',
    re.DOTALL,
)


def main() -> None:
    for path in FILES:
        html = path.read_text(encoding="utf-8")
        if not PAT.search(html):
            raise RuntimeError(f"style block not found in {path.name}")
        html = PAT.sub(SNIPPET.strip(), html, count=1)
        path.write_text(html, encoding="utf-8")
        print(f"Updated {path.name}")


if __name__ == "__main__":
    main()
