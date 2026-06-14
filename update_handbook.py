#!/usr/bin/env python3
"""Apply handbook content/structure updates (text, layout, day 0, galleries)."""

import re
from pathlib import Path

HTML = Path(__file__).parent / "多洛米蒂旅遊手冊.html"

# Shortened day intros (~60% of original)
INTROS = {
    0: "長途航班抵達米蘭，正式展開這趟義、斯、奧之旅。今天不趕行程——入住後可在主教座堂一帶散步，或到 Navigli 運河區吃頓晚餐、調時差。明天才搭火車前往威尼斯。",
    1: "從米蘭轉乘火車進入威尼斯，這是旅程真正的起點。下午放完行李，沿大運河外圍或 Castello 水巷散步；傍晚光線斜照、遊客漸少，最能感受這座無車之城。",
    2: "潟湖外島各有個性：穆拉諾玻璃、布拉諾彩屋、麗都海灘。搭 water bus 一日票串三島，節奏悠閒。記得確認末班船，傍晚留時間回主島。",
    3: "租車啟程，跨入斯洛維尼亞。順路參觀米拉馬雷城堡，再探什科茨揚洞穴，傍晚抵達懸崖上的皮蘭——舊城禁行，車停 P1/P2 再步行。",
    4: "上午走波斯托伊納洞窟與普雷德加馬城堡，下午約 50 分鐘車程到盧比安納。在 Ljubljanica 河畔與三橋一帶散步，傍晚回民宿。",
    5: "悠閒湖區日。布萊德湖是招牌明信片，可登島或繞湖；人潮多就改往博希尼湖。記得嚐一塊 kremšnita 奶油蛋糕。",
    6: "正式進山。北上可選 Orrido dello Slizza 短健行或聖坎迪多午餐，下午衝三峰全景與布拉耶斯湖——後者 16:00 後才可開車進入。",
    7: "北上約兩小時越境因斯布魯克。搭北鏈纜車至 Hafelekar，日落前回 Seegrube 看金山；其餘時間逛黃金屋頂與因河彩屋。",
    8: "加爾代納山谷從奧蒂塞伊出發，串連 Resciesa 與 Mont Seuc 草坡。體力夠可另排塞切達刀刃山脊——多洛米蒂最經典構圖之一。",
    9: "塞拉山組環繞多座山谷。Plan de Gralba 三段纜車登 Passo Sella，穿越 Città dei Sassi 巨石陣，遠眺朗科費爾巨牆。",
    10: "薩索隆戈山如垂直石牆矗立谷西。從奧蒂塞伊依天氣決定上山下山，纜車可組輕鬆或進階兩種走法；午後留意雷陣雨。",
    11: "聖克里斯蒂娜是山谷最寧靜的小鎮。Monte Pana 纜車串連吊椅与步道，升至牧場正對 Langkofel 与 Sella——適合慢午餐、躺草坡。",
    12: "卡雷扎湖號稱彩虹湖，清晨无風時倒影最美，繞湖約兩小時。陰天可改波爾查諾市區閒晃、補給起司火腿。",
    13: "塞爾瓦是山谷海拔最高的一鎮。Ciampinoi 短登 lunch 山屋，Dantercepies 走 Promenade Cir 約一小時，飽覽 Sassolungo 与 Sella。",
    14: "富內斯山谷是全行程最耗體力的一天——無纜車。8:30 前到聖瑪格達萊納教堂順光拍照，再走 Adolf Munkel 環線約 4 小時。",
    15: "還車日。維羅納停留约兩小時買起司，再赴威尼斯還車，16:00 火車到米蘭收尾。",
    16: "米蘭最後自由日：大教堂、艾曼紐二世迴廊、Brera 區，補伴手禮与 gelato。",
    17: "10:45 早班機，清晨出發。前一晚確認 Malpensa/Linate 交通，整理行李、預約計程車或查快線時刻。",
}

# Extra collapsible stories for compact / important days: list of (title, body)
EXTRA_SPOTLIGHTS = {
    3: [
        (
            "米拉馬雷城堡 · Castello di Miramare",
            "1856 年為奧地利大公馬西米連諾所建，白堡矗立在的里雅斯特灣的懸崖上，花園與步道面向亞得里亞海。大公後來出任墨西哥皇帝，1867 年在那裡被處決；城堡保留他當年的寢居，從露台望海，仍能感受十九世紀哈布斯堡世界的余韻。",
        ),
        (
            "皮蘭 · Piran",
            "這座濱海小鎮與威尼斯同屬曾經的威尼斯共和國，老城緊貼海岬，塔爾蒂尼廣場呈現完美的貝殼形。爬城牆可 360 度望見斯洛維尼亞、義大利與克羅埃西亞的海岸線——三國海水在同一片視野里交會。",
        ),
    ],
    4: [
        (
            "波斯托伊納洞窟 · Postojna Cave",
            "歐洲第二大對外開放溶洞，遊客先搭地下小火車深入，再步行穿越鐘乳石大廳。洞內棲息稀有盲蝦（人魚）Proteus anguinus，俗稱「人魚」，是斯洛維尼亞的國寶級生物。洞内恆溫約 8–10°C，務必穿暖。",
        ),
    ],
    6: [
        (
            "布拉耶斯湖 · Lago di Braies",
            "翡翠色湖水嵌在 Seekofel 山腳，木船與湖岸小教堂入鏡即明信片。為控制車流，夏季白天需預約或改搭接駁；你們 16:00 後自駕進入正好錯峰。環湖平路約 3.5 公里，適合日落前慢慢走。",
        ),
    ],
    7: [
        (
            "北鏈纜車 · Nordkette",
            "從市區 20 分鐘內直達 2300 公尺，是少數「城市與雪線同框」的纜車。設計師 Zaha Hadid 設計的 Hungerburg 站如太空艦橋；若只選一站看日落，Seegrube 的咖啡座面對 Inntal 谷與蒂羅爾主峰，是本地人的秘密。",
        ),
    ],
    14: [
        (
            "Adolf Munkel 步道",
            "這條環線穿過蓋斯勒群峰（Odle）北麓的牧场，全程約 4 小時、爬升 500 公尺。Geisler Alm 山屋可中途午餐，步道大部分在树荫与草坡間，是親近 Odle 巨墙最從容的方式——比塞切達更安靜，也更耗體力。",
        ),
    ],
}

# 4th gallery image (Wikimedia) per day; day 1 includes replacement for duplicate slot 3
FOURTH_IMAGES = {
    0: [
        ("米蘭主教座堂", "Cathedrale%20duomo%2C%20Milan.JPG?width=900"),
        ("艾曼紐二世迴廊", "Galleria%20Vittorio%20Emanuele%20II%20(Milan)%20-%20Interior.jpg?width=900"),
        ("米蘭中央車站", "Milano%20Centrale%20railway%20station%20in%202022.jpg?width=900"),
        ("Navigli 運河", "Navigli%20(Milan).jpg?width=900"),
    ],
    1: [
        ("威尼斯日落", "Tramonto%20su%20San%20Marco%20Venezia.jpg?width=900"),
        ("大運河", "The%20Grand%20Canal%2C%20Venice%202016.jpg?width=900"),
        ("里亞托橋", "Ponte%20di%20Rialto%20-%20Venice.jpg?width=900"),
        ("威尼斯水巷", "Venice%20canal%20view.jpg?width=900"),
    ],
}

# For days 2-17 only need 4th image URL (first 3 stay in HTML)
FOURTH_ONLY = {
    2: ("穆拉諾玻璃", "Murano%20Glass%20Factory%20-%20Murano%2C%20Italy.jpg?width=900"),
    3: ("的里雅斯特灣", "Gulf%20of%20Trieste%20from%20Miramare.jpg?width=900"),
    4: ("盧比安納城堡", "Ljubljana%20Castle%20view.jpg?width=900"),
    5: ("布萊德城堡", "Bled%20Castle%20Slovenia.jpg?width=900"),
    6: ("多比亞科湖", "Lake%20Dobbiaco%20(Toblach).jpg?width=900"),
    7: ("因斯布魯克舊城", "Innsbruck%20Altstadt.jpg?width=900"),
    8: ("Val Gardena 谷地", "Val%20Gardena%20Gr%C3%B6den%20S%C3%BCd%20Tirol.jpg?width=900"),
    9: ("Pordoi 山口", "Passo%20Pordoi%20Dolomites.jpg?width=900"),
    10: ("刀背山近景", "Sassolungo%20from%20Passo%20Gardena.jpg?width=900"),
    11: ("Monte Pana 牧場", "Mont%20Pana%20S%C3%BCd%20Tirol.jpg?width=900"),
    12: ("波爾查諾", "Bolzano%20Bozen%20panorama.jpg?width=900"),
    13: ("Gardena 山口", "Passo%20Gardena%20Dolomites.jpg?width=900"),
    14: ("Geisler 群峰", "Geisler%20group%20from%20Adolf%20Munkel%20trail.jpg?width=900"),
    15: ("茱麗葉陽台", "Casa%20di%20Giulietta%20Verona.jpg?width=900"),
    16: ("斯福爾扎城堡", "Milano%20Castello%20Sforzesco.jpg?width=900"),
    17: ("三峰再見", "Tre%20cime%20di%20Lavaredo.jpg?width=900"),
}

# Days 11 & 17 need 3rd image too (only had 2)
THIRD_IMAGES = {
    11: ("Ortisei 鎮景", "Urtij%C3%ABi%20Ortisei.jpg?width=900"),
    17: ("馬爾彭薩機場", "Malpensa%20airport%20terminal%201.jpg?width=900"),
}

WIKI = "https://commons.wikimedia.org/wiki/Special:FilePath/"


def wiki(frag: str) -> str:
    return WIKI + frag


def img_cell(alt: str, url: str) -> str:
    return (
        f'<span class="cell"><img alt="{alt}" '
        f'src="{url}" onerror="this.style.display=\'none\'"></span>'
    )


def spotlight(title: str, body: str) -> str:
    return (
        f'<details class="spotlight">'
        f'<summary class="lab">{title}</summary>'
        f'<div class="spotlight__body">{body}</div></details>'
    )


def convert_spotlights(html: str) -> str:
    def repl(m: re.Match) -> str:
        return spotlight(m.group(1), m.group(2))

    return re.sub(
        r'<div class="spotlight"><span class="lab">([^<]+)</span>([^<]+)</div>',
        repl,
        html,
    )


def replace_intro(html: str, day: int, text: str) -> str:
    pat = rf'(<article class="day reveal">\s*<div class="day__rail"><div class="day__num serif">{day:02d}.*?<p class="day__intro">)[^<]+(</p>)'
    return re.sub(pat, rf"\1{text}\2", html, count=1, flags=re.S)


def add_extra_spotlights(html: str, day: int, items: list) -> str:
    extra = "\n        ".join(spotlight(t, b) for t, b in items)
    pat3 = (
        rf'(<div class="day__num serif">{day:02d}[\s\S]*?'
        rf'<p class="day__intro">[^<]+</p>\s*)'
        rf'(<details class="spotlight">[\s\S]*?</details>\s*)'
        rf'(<ul class="plan">)'
    )
    return re.sub(pat3, rf"\1\2        {extra}\n        \3", html, count=1)


def rebuild_gallery(html: str, day: int, cells: list[str]) -> str:
    gallery = '<div class="gallery">\n          ' + "\n          ".join(cells) + "\n        </div>"
    pat = rf'(<div class="day__num serif">{day:02d}[\s\S]*?)<div class="gallery[^"]*">[\s\S]*?</div>'
    return re.sub(pat, rf"\1{gallery}", html, count=1)


def extract_gallery_cells(block: str) -> list[str]:
    return re.findall(r'<span class="cell">[\s\S]*?</span>', block)


def day_block(html: str, day: int) -> str | None:
    m = re.search(
        rf'<article class="day reveal">\s*<div class="day__rail"><div class="day__num serif">{day:02d}[\s\S]*?</article>',
        html,
    )
    return m.group(0) if m else None


def main() -> None:
    html = HTML.read_text(encoding="utf-8")

    # --- CSS ---
    html = html.replace(
        ".gallery{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:16px 0 6px;}",
        ".gallery{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:16px 0 6px;}",
    )
    html = re.sub(r"  \.gallery\.two\{[^}]+\}\n", "", html)

    html = html.replace(
        ".spotlight{background:linear-gradient(135deg,rgba(44,122,130,.08),rgba(217,99,63,.06));\n"
        "    border-left:3px solid var(--teal);border-radius:0 12px 12px 0;\n"
        "    padding:14px 17px;margin:14px 0 6px;font-size:14.5px;line-height:1.72;}\n"
        "  .spotlight .lab{font-family:\"DM Mono\",monospace;font-size:10.5px;letter-spacing:.14em;\n"
        "    text-transform:uppercase;color:var(--teal);display:block;margin-bottom:7px;}",
        ".spotlight{background:linear-gradient(135deg,rgba(44,122,130,.08),rgba(217,99,63,.06));\n"
        "    border-left:3px solid var(--teal);border-radius:0 12px 12px 0;\n"
        "    margin:10px 0 6px;font-size:14.5px;line-height:1.72;}\n"
        "  .spotlight summary.lab{font-family:\"DM Mono\",monospace;font-size:10.5px;letter-spacing:.14em;\n"
        "    text-transform:uppercase;color:var(--teal);display:flex;align-items:center;justify-content:space-between;\n"
        "    padding:12px 17px;cursor:pointer;list-style:none;user-select:none;}\n"
        "  .spotlight summary.lab::-webkit-details-marker{display:none;}\n"
        "  .spotlight summary.lab::after{content:'＋';font-size:14px;color:var(--glow);transition:transform .2s;}\n"
        "  .spotlight[open] summary.lab::after{content:'－';}\n"
        "  .spotlight__body{padding:0 17px 14px;}\n"
        "  .spotlights{margin:8px 0;}",
    )
    html = html.replace(
        "  .chapter[style*=\"spruce\"] ~ .chapter .spotlight .lab{color:var(--glow);}",
        "  .chapter[style*=\"spruce\"] ~ .chapter .spotlight summary.lab{color:var(--glow);}",
    )

    html = re.sub(
        r"  @media\(max-width:600px\)\{[^}]*\.gallery\{grid-template-columns:repeat\(2,1fr\);\}\n",
        "",
        html,
    )
    html = html.replace(
        "  @media(max-width:600px){",
        "  @media(max-width:600px){\n    .gallery{grid-template-columns:repeat(2,1fr);}",
    )

    # remove tipsband
    html = re.sub(r"  \.tipsband[^{]*\{[^}]*\}\n", "", html)
    html = re.sub(r"  \.tipsband [^{]*\{[^}]*\}\n", "", html)
    html = re.sub(r"  \.tipgrid\{[^}]+\}\n", "", html)
    html = re.sub(r"  \.tip\{[^}]+\}\n", "", html)
    html = re.sub(r"  \.tip [^{]*\{[^}]*\}\n", "", html)
    html = re.sub(r"    \.tipsband[^\n]+\n", "", html)
    html = re.sub(r"<section class=\"tipsband\">[\s\S]*?</section>\n\n", "", html)

    # hero stats & dates
    html = html.replace('<div class="n mono">17</div>', '<div class="n mono">18</div>')
    html = html.replace(
        '<div class="scrollcue">↓ 6/29 – 7/16</div>',
        '<div class="scrollcue">↓ Day 0 – 7/16</div>',
    )
    html = html.replace(
        "Day 1 – 2 · 潟湖、玻璃島与彩虹島",
        "Day 0 – 2 · 米蘭、潟湖與外島",
    )
    html = html.replace(
        "Day 6 – 14 · 纜車、步道、巨石与孤獨教堂",
        "Day 7 – 15 · 纜車、步道、巨石与孤獨教堂",
    )
    html = html.replace(
        "Day 15 – 17 · 起司、購物与回程",
        "Day 16 – 18 · 起司、購物與回程",
    )
    html = html.replace(
        "多洛米蒂 · 2026.06.29 – 07.16",
        "多洛米蒂 · 2026.06.29 – 07.16 · 18 天",
    )

    # convert spotlights before day edits
    html = convert_spotlights(html)

    # --- Day 0 insert before Day 01 ---
    day0 = f"""
    <article class="day reveal">
      <div class="day__rail"><div class="day__num serif">00<small>DAY</small></div><div class="day__date">6/29 一<br>Jun 29</div></div>
      <div class="day__body">
        <h3 class="day__city serif">抵達 · 米蘭</h3><span class="day__tag">飛行日</span>
        <div class="gallery">
          {img_cell(*FOURTH_IMAGES[0][0])}
          {img_cell(*FOURTH_IMAGES[0][1])}
          {img_cell(*FOURTH_IMAGES[0][2])}
          {img_cell(*FOURTH_IMAGES[0][3])}
        </div>
        <p class="galcap">米蘭主教座堂 · 艾曼紐二世迴廊 · 中央車站 · Navigli 運河</p>
        <p class="day__intro">{INTROS[0]}</p>
        {spotlight("米蘭 · 北義門戶", "米蘭是義大利金融与時尚中心，卻常被當成轉運站。其實主教座堂广场、艾曼紐二世迴廊与 Navigli 運河區，足以用半天認識這座城市——不必買票進每座教堂，在拱廊下喝杯 espresso、看電車叮叮駛過，就是標準米蘭節奏。")}
        <ul class="plan">
          <li><span class="dur">—</span><span class="ic">✈️</span>抵達米蘭（Malpensa / Linate）</li>
          <li><span class="dur">PM</span>入住、市區或 Navigli 晚餐、早休息</li>
        </ul>
      </div>
    </article>

"""
    day0 = day0.replace(
        img_cell(*FOURTH_IMAGES[0][0]),
        img_cell(FOURTH_IMAGES[0][0][0], wiki(FOURTH_IMAGES[0][0][1])),
    )
    for alt, frag in FOURTH_IMAGES[0]:
        day0 = day0.replace(
            img_cell(alt, wiki(frag)) if wiki(frag) else "",
            img_cell(alt, wiki(frag)),
        )

    # rebuild day0 gallery properly
    d0_cells = [img_cell(alt, wiki(frag)) for alt, frag in FOURTH_IMAGES[0]]
    day0 = f"""
    <article class="day reveal">
      <div class="day__rail"><div class="day__num serif">00<small>DAY</small></div><div class="day__date">6/29 一<br>Jun 29</div></div>
      <div class="day__body">
        <h3 class="day__city serif">抵達 · 米蘭</h3><span class="day__tag">飛行日</span>
        <div class="gallery">
          {chr(10).join('          ' + c for c in d0_cells)}
        </div>
        <p class="galcap">米蘭主教座堂 · 艾曼紐二世迴廊 · 中央車站 · Navigli 運河</p>
        <p class="day__intro">{INTROS[0]}</p>
        {spotlight("米蘭 · 北義門戶", "米蘭是義大利金融與時尚中心，卻常被當成轉運站。其實主教座堂廣場、艾曼紐二世迴廊與 Navigli 運河區，足以用半天認識這座城市——在拱廊下喝杯 espresso、看電車叮叮駛過，就是標準米蘭節奏。")}
        <ul class="plan">
          <li><span class="dur">—</span><span class="ic">✈️</span>抵達米蘭（Malpensa / Linate）</li>
          <li><span class="dur">PM</span>入住、市區或 Navigli 晚餐、早休息</li>
        </ul>
      </div>
    </article>
"""
    html = html.replace(
        '<div class="chapter__head reveal">\n      <div class="num">CH.01</div>',
        day0 + '    <div class="chapter__head reveal">\n      <div class="num">CH.01</div>',
        1,
    )

    # fix simplified chars in day0
    html = html.replace("金融与時尚", "金融與時尚")

    # intros for days 1-17
    for d in range(1, 18):
        html = replace_intro(html, d, INTROS[d])

    # extra spotlights
    for d, items in EXTRA_SPOTLIGHTS.items():
        html = add_extra_spotlights(html, d, items)

    # galleries: day 1 full rebuild with wiki urls for new imgs; others append 4th
    d1_cells = [img_cell(alt, wiki(frag)) for alt, frag in FOURTH_IMAGES[1]]
    html = rebuild_gallery(html, 1, d1_cells)

    for d in range(2, 18):
        block = day_block(html, d)
        if not block:
            continue
        cells = extract_gallery_cells(block)
        if d in THIRD_IMAGES and len(cells) == 2:
            alt, frag = THIRD_IMAGES[d]
            cells.append(img_cell(alt, wiki(frag)))
        if d in FOURTH_ONLY and len(cells) < 4:
            alt, frag = FOURTH_ONLY[d]
            cells.append(img_cell(alt, wiki(frag)))
        while len(cells) > 4:
            cells.pop()
        html = rebuild_gallery(html, d, cells)

    HTML.write_text(html, encoding="utf-8")
    print("Structure update done. Run embed_images.py for new Wikimedia URLs.")


if __name__ == "__main__":
    main()
