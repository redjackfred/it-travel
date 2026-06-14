#!/usr/bin/env python3
"""Patch Day 0 / Day 1 itinerary text and intro disclaimer."""

import re
from pathlib import Path

HTML = Path(__file__).parent / "多洛米蒂旅遊手冊.html"

DISCLAIMER = """
    <div class="note reveal" style="margin-top:28px;">
      <span class="lab">小提醒</span>
      歐洲突發狀況多，所以行程不敢排太滿；為了避免太趕，整體安排也比較鬆散，留一點彈性應付延誤或臨時想多待的地方。
    </div>"""

DAY0_BODY = """        <h3 class="day__city serif">台北 ×3 · 日本 ×1 <span class="arrow">→</span> 機上</h3><span class="day__tag">飛行日</span>
        GALLERY_PLACEHOLDER
        <p class="galcap">三人桃園出發 · 一人日本出發 · 機上度過</p>
        <p class="day__intro">三人從台北出發，一人從日本出發；四人各自搭乘長途航班，在機上度過這一天。補充睡眠、調整時差，明天約 08:45 在米蘭機場會合。</p>
        <details class="spotlight"><summary class="lab">長途航班 · 分頭出發</summary><div class="spotlight__body">跨洲航班動輒十幾小時，記得多喝水、定時起身活動。從日本出發的那位，留意航班時間是否與台北三人銜接同一班抵達米蘭。機上盡量依義大利時間小睡，落地後會順很多——行李、入境與前往中央車站，四人確認一下動線即可。</div></details>
        <ul class="plan">
          <li><span class="dur">—</span><span class="ic">✈️</span>三人台北出發 · 一人日本出發</li>
          <li><span class="dur">—</span>長途航班，機上度過</li>
        </ul>"""

DAY1_BODY = """        <h3 class="day__city serif">米蘭 <span class="arrow">→</span> 威尼斯</h3>
        GALLERY_PLACEHOLDER
        <p class="galcap">米蘭機場 · 中央車站 · 威尼斯本島</p>
        <p class="day__intro">08:45 抵達米蘭機場，搭快線或區域鐵路至中央車站，車站附近簡單中餐後轉搭火車前往威尼斯，約 15:00 抵達本島。下午放行李，沿大運河或 Castello 水巷散步。</p>
        <details class="spotlight"><summary class="lab">聖馬可廣場 · Piazza San Marco</summary><div class="spotlight__body">威尼斯的心臟曾被稱為「歐洲的客廳」。拿破崙曾感嘆這是「世上最美的會客廳」。廣場周圍的聖馬可大教堂融合了拜占庭、哥德與文藝復興風格，外牆馬賽克在夕陽下閃著金綠色光澤。若時間有限，在廣場邊的咖啡座看鴿子與遊人來去，也是經典的威尼斯體驗——只是價格不菲，本地人多半在巷弄小酒吧用站著的方式（al banco）喝一杯。</div></details>
        <ul class="plan">
          <li><span class="dur">08:45</span><span class="ic">✈️</span>抵達米蘭機場（Malpensa / Linate）</li>
          <li><span class="dur">AM</span><span class="ic">🚄</span>機場快線至米蘭中央車站、中餐</li>
          <li><span class="dur">午後</span><span class="ic">🚄</span>火車米蘭 → 威尼斯本島（約 15:00 抵達）</li>
          <li><span class="dur">PM</span>放行李，沿水巷散步、看夕陽</li>
        </ul>
        <div class="note"><span class="lab">吃什麼</span>義式冰淇淋 · 披薩 · 一歐元站著小食配酒 · 炸海鮮拼盤（fritto misto）。</div>"""


def extract_gallery(article: str) -> str:
    m = re.search(r'(<div class="gallery">.*?</div>)', article, re.DOTALL)
    if not m:
        raise RuntimeError("gallery not found")
    return m.group(1)


def patch_day(html: str, day_num: str, new_body: str) -> str:
    pat = rf'(<article class="day reveal">\s*<div class="day__rail"><div class="day__num serif">{day_num}<small>DAY</small></div>.*?</div>\s*<div class="day__body">\s*).*?(</div>\s*</article>)'
    m = re.search(pat, html, re.DOTALL)
    if not m:
        raise RuntimeError(f"Day {day_num} article not found")
    gallery = extract_gallery(m.group(0))
    body = new_body.replace("GALLERY_PLACEHOLDER", gallery)
    return html[: m.start()] + m.group(1) + body + m.group(2) + html[m.end() :]


def main() -> None:
    html = HTML.read_text(encoding="utf-8")

    if "歐洲突發狀況多" not in html:
        html = html.replace(
            '    <div class="route reveal">',
            DISCLAIMER + '\n    <div class="route reveal">',
            1,
        )

    html = html.replace(
        '<div class="meta">Day 0 – 2 · 米蘭、潟湖與外島</div>',
        '<div class="meta">Day 0 – 2 · 出發、米蘭轉威尼斯與外島</div>',
    )

    html = patch_day(html, "00", DAY0_BODY)
    html = patch_day(html, "01", DAY1_BODY)

    HTML.write_text(html, encoding="utf-8")
    print("Patched Day 0, Day 1, and intro disclaimer.")


if __name__ == "__main__":
    main()
