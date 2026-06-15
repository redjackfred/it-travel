#!/usr/bin/env python3
"""Strip leading zeros from single-digit day numbers in handbook HTML."""

import re
from pathlib import Path

ROOT = Path(__file__).parent
FILES = [ROOT / "多洛米蒂旅遊手冊.html", ROOT / "index.html"]

DAY_PAT = re.compile(
    r'(<div class="day__num serif">)(\d{2})(<small>DAY</small></div>)'
)


def main() -> None:
    for path in FILES:
        html = path.read_text(encoding="utf-8")

        def repl(m: re.Match[str]) -> str:
            return f"{m.group(1)}{int(m.group(2))}{m.group(3)}"

        html, n = DAY_PAT.subn(repl, html)
        path.write_text(html, encoding="utf-8")
        print(f"Updated {n} day numbers in {path.name}")


if __name__ == "__main__":
    main()
