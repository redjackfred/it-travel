#!/usr/bin/env python3
"""Download unique Wikimedia Commons images for the travel handbook."""

import hashlib
import io
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

HTML_PATH = Path(__file__).parent / "多洛米蒂旅遊手冊.html"
CACHE_DIR = Path(__file__).parent / ".img-cache-v2"
GALLERY_MAX = 720
HERO_MAX = 1200
JPEG_QUALITY = 78
DELAY = 3.5
UA = "TravelHandbook/2.0 (+https://it-travel.peiwen.dev)"

# 18 days × 4 unique Commons filenames
DAY_IMAGES: dict[int, list[tuple[str, str]]] = {
    0: [
        ("米蘭主教座堂", "Cathedrale duomo, Milan.JPG"),
        ("艾曼紐二世迴廊", "Galleria Vittorio Emanuele II (Milan) - Interior.jpg"),
        ("米蘭中央車站", "Milano Centrale railway station.jpg"),
        ("Navigli 運河", "Canal Nord Navigli - Milan (IT25) - 2022-09-02 - 5.jpg"),
    ],
    1: [
        ("聖馬可廣場日落", "Tramonto su San Marco Venezia.jpg"),
        ("威尼斯大運河", "The Grand Canal, Venice 2016.jpg"),
        ("里亞托橋", "Ponte di Rialto Venice 1.jpg"),
        ("威尼斯 gondola", "Venice Gondola Grand Canal.jpg"),
    ],
    2: [
        ("布拉諾彩屋", "Burano - Rio di Terranova and Fondamenta Terranova from Ponte Vigna, to south.jpg"),
        ("布拉諾運河", "Burano-Venezia-DSCF0001.JPG"),
        ("麗都海灘", "Beach vendor Lido di Venezia.jpg"),
        ("穆拉諾島", "Faro (Murano).jpg"),
    ],
    3: [
        ("米拉馬雷城堡", "Castello di Miramare.JPG"),
        ("什科茨揚洞穴", "Skocjan Caves (3802558032).jpg"),
        ("皮蘭全景", "Piran slovenia (48885787638).jpg"),
        ("塔爾蒂尼廣場", "Tartini Square in Piran.jpg"),
    ],
    4: [
        ("波斯托伊納洞窟", "Postojna Cave - Slovenia.jpg"),
        ("普雷德加馬城堡", "Predjama-Castle-2021-Luka-Peternel.jpg"),
        ("盧比安納三橋", "Ljubljana - Tromostovje (48749472426).jpg"),
        ("盧比安納龍橋", "Dragon Ljubljana.jpg"),
    ],
    5: [
        ("布萊德湖", "View of Bled Island from the south, 2013.jpg"),
        ("布萊德湖心島", "Bled island July 2005.jpg"),
        ("博希尼湖", "Bohinj-jezero-Naklova glava.JPG"),
        ("布萊德城堡", "Bled Castle 05.jpg"),
    ],
    6: [
        ("布拉耶斯湖", "Lago di braies 7.JPG"),
        ("三峰全景", "Drei Zinnen Tre Cime di Lavaredo Dolomites.jpg"),
        ("三峰夕照", "Tramonto Tre cime di Lavaredo.jpg"),
        ("多比亞科湖", "Toblach Toblacher See 02.jpg"),
    ],
    7: [
        ("因河彩屋", "Inn and Mariahilfstraße seen from Herzog-Siegmund-Ufer Innsbruck 2023-09-23 01.jpg"),
        ("黃金屋頂", "Goldenes Dachl (Innsbruck).jpg"),
        ("北鏈纜車", "Hafelekar, Tyrol, Austria - panoramio.jpg"),
        ("因斯布魯克全景", "Innsbruck Panorama Nordkette 3.jpg"),
    ],
    8: [
        ("塞切達山脊", "The famous Secëda-Alm Ridgeline located in South Tyrol, Italy.jpg"),
        ("塞切達群峰", "The Dolomites from Seceda.jpg"),
        ("塞切達眺望", "Zillertal Alps - View from Seceda.jpg"),
        ("奧蒂塞伊鎮", "Erwin Merlet - Poster Ortisei Val Gardena.jpg"),
    ],
    9: [
        ("塞拉山口", "Langkofel group from the Sella pass 2016.jpg"),
        ("Passo Sella", "Passo sella (36889542731).jpg"),
        ("Sella 全景", "Passo Sella (2240 mt) - panoramio.jpg"),
        ("Pordoi 山口", "Passo Pordoi 02.jpg"),
    ],
    10: [
        ("朗科費爾山", "Passo Sella - verso il Sassolungo.jpg"),
        ("Sassolungo 纜車", "Telecabin Forcella del Sassolungo - gondola.jpg"),
        ("Sella 巨牆", "Passo Sella (2240 mt) - panoramio - Michael Paraskevas.jpg"),
        ("Langkofel 群峰", "Rifugio Sassopiatto.jpg"),
    ],
    11: [
        ("Col Raiser 山屋", "Vista dal rifugio Col Raiser (3166821108).jpg"),
        ("Seceda 與 Pic", "Urtijei Seceda and Pic.JPG"),
        ("Val Gardena 海報", "Unika Val Gardena dedite3 Urtijëi 2021.jpg"),
        ("聖克里斯蒂娜", "Santa Cristina Gherdëina.jpg"),
    ],
    12: [
        ("Carezza 與 Latemar", "Lago di Carezza and Latemar, Carezza, Trentino-Alto Adige, Italy, 2025 October.jpg"),
        ("Carezza 與 Catinaccio", "Lago di Carezza and Catinaccio group peaks, Carezza, Trentino-Alto Adige, Italy, 2025 October.jpg"),
        ("卡雷扎湖", "Lago Carezza.JPG"),
        ("波爾查諾", "Bolzano, Italy.jpg"),
    ],
    13: [
        ("Sella 山口", "Maratona dles Dolomites - Sella Pass.jpg"),
        ("馬爾莫拉達峰", "Marmolada - panoramio (6).jpg"),
        ("多洛米蒂全景", "Panorama from Belvedere Dolomites.jpg"),
        ("Gardena 山口", "Seiser Alm 01.jpg"),
    ],
    14: [
        ("聖瑪格達萊納教堂", "La chiesa di S. Maddalena e le Odle sullo sfondo.jpg"),
        ("聖喬凡尼教堂", "San giovanni.JPG"),
        ("富內斯山谷", "1 dolomites santa magdalena 2024 val di funes.jpg"),
        ("蓋斯勒群峰", "Odle di Funes.jpg"),
    ],
    15: [
        ("維羅納競技場", "Arena di Verona 2.jpg"),
        ("競技場外觀", "Arena, Verona.JPG"),
        ("競技場內部", "Verona Italy arena DSC08030.JPG"),
        ("茱麗葉陽台", "Casa di Giulietta Verona.jpg"),
    ],
    16: [
        ("米蘭大教堂夜景", "Duomo di Milano by night (44602863405).jpg"),
        ("艾曼紐拱廊外觀", "Galleria Vittorio Emanuele II (Milan) - Exterior.jpg"),
        ("主教座堂廣場", "Galleria Vittorio Emanuele II e piazza duomo.jpg"),
        ("斯福爾扎城堡", "Castello Sforzesco.jpg"),
    ],
    17: [
        ("三峰再會", "Tre cime di Lavaredo.jpg"),
        ("米蘭天際線", "Milano - Duomo - panoramio.jpg"),
        ("馬爾彭薩機場", "MXP airport.jpg"),
        ("阿爾卑斯雲海", "Above the clouds.jpg"),
    ],
}

HERO_FILE = "Drei Zinnen Tre Cime di Lavaredo Dolomites.jpg"


def download(filename: str, is_hero: bool = False) -> bytes:
    max_w = HERO_MAX if is_hero else GALLERY_MAX
    cache_key = hashlib.sha256(f"{filename}|{max_w}".encode()).hexdigest()[:16]
    cache = CACHE_DIR / f"{cache_key}.jpg"
    if cache.exists():
        return cache.read_bytes()

    encoded = urllib.parse.quote(filename.replace(" ", "_"), safe="/()'-,")
    # Special:FilePath handles spaces; use quote with safe chars for filenames with commas
    url = (
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        + urllib.parse.quote(filename, safe="(),'-")
        + f"?width={max_w}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                raw = resp.read()
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(DELAY * (attempt + 2))
                continue
            raise FileNotFoundError(f"{filename}: HTTP {e.code}") from e
    else:
        raise RuntimeError(f"Failed after retries: {filename}")

    img = Image.open(io.BytesIO(raw))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    w, h = img.size
    if w > max_w:
        img = img.resize((max_w, int(h * max_w / w)), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    data = buf.getvalue()
    CACHE_DIR.mkdir(exist_ok=True)
    cache.write_bytes(data)
    time.sleep(DELAY)
    return data


def to_data_uri(data: bytes) -> str:
    import base64

    return "data:image/jpeg;base64," + base64.b64encode(data).decode("ascii")


def img_cell(alt: str, uri: str) -> str:
    return (
        f'<span class="cell"><img alt="{alt}" '
        f'src="{uri}" onerror="this.style.display=\'none\'"></span>'
    )


def rebuild_gallery(html: str, day: int, cells: list[str]) -> str:
    gallery = '<div class="gallery">\n          ' + "\n          ".join(cells) + "\n        </div>"
    pat = rf'(<div class="day__num serif">{day:02d}[\s\S]*?)<div class="gallery">[\s\S]*?</div>'
    return re.sub(pat, rf"\1{gallery}", html, count=1)


FOOTER = """
  </div>
</section>

<footer class="end">
  <div class="wrap">
    <p class="serif">山，等你來。</p>
    <p>多洛米蒂 · 2026.06.29 – 07.16 · 照片來源：Wikimedia Commons</p>
  </div>
</footer>

<script>
  (function(){
    document.querySelectorAll('.cell img').forEach(function(img){
      img.addEventListener('error',function(){img.style.display='none';});
    });
    var els=document.querySelectorAll('.reveal');
    if(!('IntersectionObserver' in window)||window.matchMedia('(prefers-reduced-motion: reduce)').matches){
      els.forEach(function(e){e.classList.add('in');});return;
    }
    var io=new IntersectionObserver(function(en){en.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}});},{threshold:.1});
    els.forEach(function(e){io.observe(e);});
  })();
</script>
</body>
</html>
"""


def repair_truncated_html(html: str) -> str:
    """Remove corrupted Day 17 tail (file was truncated mid-base64) and restore footer."""
    marker = '<article class="day reveal">\n      <div class="day__rail"><div class="day__num serif">17'
    if marker not in html:
        if html.rstrip().endswith("</html>"):
            return html
        raise RuntimeError("Day 17 marker not found and HTML is not complete")
    if html.rstrip().endswith("</html>"):
        return html
    print("Repairing truncated Day 17 …")
    return html[: html.index(marker)]


def build_day17_article(cells: list[str]) -> str:
    gallery = '<div class="gallery">\n          ' + "\n          ".join(cells) + "\n        </div>"
    return f"""    <article class="day reveal">
      <div class="day__rail"><div class="day__num serif">17<small>DAY</small></div><div class="day__date">7/16 四<br>Jul 16</div></div>
      <div class="day__body">
        <h3 class="day__city serif">機場 <span class="arrow">→</span> 回程</h3>
        {gallery}
        <p class="galcap">三峰再會 · 米蘭天際線 · 馬爾彭薩機場</p>
        <p class="day__intro">10:45 早班機，清晨出發。前一晚確認 Malpensa/Linate 交通，整理行李、預約計程車或查快線時刻。</p>
        <ul class="plan">
          <li><span class="dur">10:45</span><span class="ic">✈️</span>早班機，預留前往機場時間</li>
        </ul>
      </div>
    </article>
{FOOTER}"""


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    html = repair_truncated_html(html)
    used_hashes: set[str] = set()
    failed: list[str] = []
    day17_cells: list[str] | None = None

    print("Downloading hero …", end=" ", flush=True)
    hero_uri = to_data_uri(download(HERO_FILE, is_hero=True))
    print("OK")

    for day, items in sorted(DAY_IMAGES.items()):
        print(f"Day {day:02d}:", end=" ", flush=True)
        cells = []
        day_data_hashes: list[str] = []
        for alt, filename in items:
            try:
                data = download(filename)
                h = hashlib.md5(data).hexdigest()
                if h in day_data_hashes:
                    raise RuntimeError(f"duplicate within day: {filename}")
                day_data_hashes.append(h)
                used_hashes.add(h)
                cells.append(img_cell(alt, to_data_uri(data)))
                print(".", end="", flush=True)
            except Exception as e:
                failed.append(f"Day {day} {filename}: {e}")
                print("x", end="", flush=True)
        if len(cells) == 4:
            if day == 17:
                day17_cells = cells
            else:
                html = rebuild_gallery(html, day, cells)
        print()

    if day17_cells is not None:
        html = html.rstrip() + "\n\n" + build_day17_article(day17_cells)

    html = re.sub(
        r'(<img class="hero__img"[^>]*src=")[^"]+(")',
        rf"\1{hero_uri}\2",
        html,
        count=1,
    )

    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"\nUnique images: {len(used_hashes)}")
    if failed:
        print("Failures:")
        for f in failed:
            print(" ", f)
        sys.exit(1)
    print(f"HTML size: {HTML_PATH.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    import sys

    main()
