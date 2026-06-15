#!/usr/bin/env python3
"""Replace intro section in handbook HTML files."""

import re
from pathlib import Path

ROOT = Path(__file__).parent
FILES = [ROOT / "多洛米蒂旅遊手冊.html", ROOT / "index.html"]

INTRO = """<section class="intro">
  <div class="wrap">
    <header class="intro__head reveal">
      <p class="intro__eyebrow"><span class="intro__eyebrow-en">The Route</span><span class="intro__eyebrow-div">·</span><span>路線概覽</span></p>
      <h2 class="intro__title serif">多洛米蒂 · 18 日環線</h2>
      <p class="intro__deck mono">2026.6.29 – 7.16 · 義大利 · 斯洛維尼亞 · 奧地利 · 18 日</p>
    </header>

    <div class="intro__prose reveal">
      <p>這本手冊記載的是一趟四人同行的夏季旅程：四人從台北出發，翌日在米蘭落地後正式啟程。前半以威尼斯的水道與外島暖身，再沿亞得里亞海畔進入斯洛維尼亞——湖國、洞窟、懸崖小鎮逐日展開；當車道開始攀上山脊，便走進<strong>多洛米蒂</strong>，也是這趟旅程真正的心臟。</p>
      <p>十天裡，纜車與步道會取代時鐘成為日常節奏；外側繞因斯布魯克看一眼北鏈，再由維羅納與米蘭徐徐收束。整體行程刻意留空——歐洲路上變數多，鬆一點，才能在對的觀景點多站十分鐘，或在不期而遇的小館前多坐半小時。</p>
    </div>

    <div class="note reveal intro__note">
      <span class="lab">小提醒</span>
      歐洲突發狀況多，所以行程不敢排太滿；為了避免太趕，整體安排也比較鬆散，留一點彈性，好應付延誤或臨時想多待一會兒的地方。
    </div>

    <div class="intro__route reveal">
      <div class="intro__route-head">
        <p class="intro__route-label">沿途一站</p>
      </div>
      <ol class="route-path">
        <li class="route-path__item"><span class="route-path__dot">1</span><span class="route-path__name">威尼斯</span></li>
        <li class="route-path__item"><span class="route-path__dot">2</span><span class="route-path__name">皮蘭</span></li>
        <li class="route-path__item"><span class="route-path__dot">3</span><span class="route-path__name">盧比安納</span></li>
        <li class="route-path__item"><span class="route-path__dot">4</span><span class="route-path__name">布萊德湖</span></li>
        <li class="route-path__item route-path__item--core"><span class="route-path__dot">5</span><span class="route-path__name">多洛米蒂</span><span class="route-path__badge">十日核心</span></li>
        <li class="route-path__item"><span class="route-path__dot">6</span><span class="route-path__name">因斯布魯克</span></li>
        <li class="route-path__item"><span class="route-path__dot">7</span><span class="route-path__name">維羅納</span></li>
        <li class="route-path__item"><span class="route-path__dot">8</span><span class="route-path__name">米蘭</span></li>
      </ol>
    </div>

    <div class="intro__map reveal">
      <div class="intro__route-head">
        <p class="intro__route-label">路線地圖</p>
      </div>
      <div id="trip-map" class="trip-map" aria-label="行程路線互動地圖"></div>
      <p class="trip-map__cap">橘色為主要停站 · 深綠為多洛米蒂細部 · 虛線為移動方向</p>
    </div>
  </div>
</section>"""

PAT = re.compile(r"<section class=\"intro\">.*?</section>", re.DOTALL)


def main() -> None:
    for path in FILES:
        html = path.read_text(encoding="utf-8")
        if not PAT.search(html):
            raise RuntimeError(f"intro section not found in {path.name}")
        html = PAT.sub(INTRO, html, count=1)
        path.write_text(html, encoding="utf-8")
        print(f"Patched intro in {path.name}")


if __name__ == "__main__":
    main()
