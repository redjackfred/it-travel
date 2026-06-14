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
      <h2 class="intro__title serif">從潟湖到白雲石</h2>
      <p class="intro__deck mono">2026.6.29 – 7.16 · 義大利 · 斯洛維尼亞 · 奧地利 · 18 日</p>
    </header>

    <div class="intro__prose reveal">
      <p>這本手冊記載的是一趟四人同行的夏季旅程：三人從台北、一人從日本出發，翌日在米蘭會合後正式啟程。前半以威尼斯的水道與外島暖身，再沿亞得里亞海畔進入斯洛維尼亞——湖國、洞窟、懸崖小鎮逐日展開；當車道開始攀上山脊，便走進<strong>多洛米蒂</strong>，也是這趟旅程真正的心臟。</p>
      <p>十天裡，纜車與步道會取代時鐘成為日常節奏；外側繞因斯布魯克看一眼北鏈，再由維羅納與米蘭徐徐收束。整體行程刻意留空——歐洲路上變數多，鬆一點，才能在對的觀景點多站十分鐘，或在不期而遇的小館前多坐半小時。</p>
    </div>

    <div class="note reveal intro__note">
      <span class="lab">小提醒</span>
      歐洲突發狀況多，所以行程不敢排太滿；為了避免太趕，整體安排也比較鬆散，留一點彈性，好應付延誤或臨時想多待一會兒的地方。
    </div>

    <div class="intro__route reveal">
      <p class="intro__route-label">沿途一站</p>
      <div class="route-track" role="list">
        <span class="route-track__stop" role="listitem"><em>01</em>威尼斯</span>
        <span class="route-track__stop" role="listitem"><em>02</em>皮蘭</span>
        <span class="route-track__stop" role="listitem"><em>03</em>盧比安納</span>
        <span class="route-track__stop" role="listitem"><em>04</em>布萊德湖</span>
        <span class="route-track__stop route-track__stop--core" role="listitem"><em>05</em>多洛米蒂<br><small>十日核心</small></span>
        <span class="route-track__stop" role="listitem"><em>06</em>因斯布魯克</span>
        <span class="route-track__stop" role="listitem"><em>07</em>維羅納</span>
        <span class="route-track__stop" role="listitem"><em>08</em>米蘭</span>
      </div>
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
