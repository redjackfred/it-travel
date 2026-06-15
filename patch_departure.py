#!/usr/bin/env python3
"""Update copy: all four travelers depart from Taipei."""

from pathlib import Path

ROOT = Path(__file__).parent
FILES = [ROOT / "多洛米蒂旅遊手冊.html", ROOT / "index.html"]

REPLACEMENTS = [
    (
        "三人從台北、一人從日本出發，翌日在米蘭會合後正式啟程",
        "四人從台北出發，翌日在米蘭落地後正式啟程",
    ),
    (
        '台北 ×3 · 日本 ×1 <span class="arrow">→</span> 機上',
        '台北 <span class="arrow">→</span> 機上',
    ),
    (
        "三人桃園出發 · 一人日本出發 · 機上度過",
        "四人桃園出發 · 機上度過",
    ),
    (
        "三人從台北出發，一人從日本出發；四人各自搭乘長途航班，在機上度過這一天。補充睡眠、調整時差，明天約 08:45 在米蘭機場會合。",
        "四人從台北出發，搭乘長途航班，在機上度過這一天。補充睡眠、調整時差，明天約 08:45 抵達米蘭機場。",
    ),
    (
        "建議三人先在桃園集合確認行李與護照",
        "建議四人先在桃園集合確認行李與護照",
    ),
    (
        '<summary class="lab">日本出發 · 日本</summary><div class="spotlight__body">從日本出發的那位，可選成田或羽田等樞紐機場，重點是抵達米蘭的時間能否與台北三人銜接。若航班不同，事先約好「哪個航廈、哪個出口」會合，比落地後才用訊息喬時間輕鬆得多。</div>',
        '<summary class="lab">四人同行 · 出發</summary><div class="spotlight__body">從同一個城市出發，行李與航班可以一起確認——護照效期、轉機時間、座位是否相鄰，在桃園集合時一次對過，飛行日會輕鬆很多。</div>',
    ),
    (
        '<summary class="lab">長途航班 · 分頭出發</summary><div class="spotlight__body">跨洲航班動輒十幾小時，記得多喝水、定時起身活動。機上盡量依義大利時間調整睡眠，落地後入境、領行李、搭快線進米蘭中央車站——四人確認動線即可，明天才是正式會合的一天。</div>',
        '<summary class="lab">長途航班 · 飛行日</summary><div class="spotlight__body">跨洲航班動輒十幾小時，記得多喝水、定時起身活動。機上盡量依義大利時間調整睡眠，落地後入境、領行李會順很多——四人同行，動線一起確認即可。</div>',
    ),
    (
        "三人台北出發 · 一人日本出發",
        "四人台北出發",
    ),
]


def main() -> None:
    for path in FILES:
        html = path.read_text(encoding="utf-8")
        original = html
        for old, new in REPLACEMENTS:
            if old not in html:
                raise RuntimeError(f"Missing expected text in {path.name}: {old[:60]}…")
            html = html.replace(old, new)
        if html == original:
            raise RuntimeError(f"No changes applied to {path.name}")
        path.write_text(html, encoding="utf-8")
        print(f"Patched {path.name}")


if __name__ == "__main__":
    main()
