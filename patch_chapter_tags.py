#!/usr/bin/env python3
"""Add consistent English taglines to all chapter headers."""

from pathlib import Path

ROOT = Path(__file__).parent
FILES = [ROOT / "多洛米蒂旅遊手冊.html", ROOT / "index.html"]

REPLACEMENTS = [
    (
        '<div class="num">CH.01</div><h2 class="serif">水都 · 威尼斯</h2>',
        '<div class="num">CH.01 · THE LAGOON</div><h2 class="serif">水都 · 威尼斯</h2>',
    ),
    (
        '<div class="num">CH.02</div><h2 class="serif">斯洛維尼亞 · 湖與洞窟</h2>',
        '<div class="num">CH.02 · EMERALD SHORE</div><h2 class="serif">斯洛維尼亞 · 湖與洞窟</h2>',
    ),
    (
        '<div class="num">CH.04</div><h2 class="serif">歸途 · 維羅納與米蘭</h2>',
        '<div class="num">CH.04 · THE FINALE</div><h2 class="serif">歸途 · 維羅納與米蘭</h2>',
    ),
]


def main() -> None:
    for path in FILES:
        html = path.read_text(encoding="utf-8")
        for old, new in REPLACEMENTS:
            if old not in html:
                raise RuntimeError(f"Missing in {path.name}: {old[:50]}…")
            html = html.replace(old, new)
        path.write_text(html, encoding="utf-8")
        print(f"Patched chapter tags in {path.name}")


if __name__ == "__main__":
    main()
