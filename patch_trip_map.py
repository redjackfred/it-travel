#!/usr/bin/env python3
"""Inject interactive Leaflet trip map into handbook HTML files."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
FILES = [ROOT / "多洛米蒂旅遊手冊.html", ROOT / "index.html"]

LEAFLET_CSS = (
    '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" '
    'integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">'
)

LEAFLET_JS = (
    '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" '
    'integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>'
)

MAP_BLOCK = """    <div class="intro__map reveal">
      <div class="intro__route-head">
        <p class="intro__route-label">路線地圖</p>
      </div>
      <div id="trip-map" class="trip-map" aria-label="行程路線互動地圖"></div>
      <p class="trip-map__cap">橘色為主要停站 · 深綠為多洛米蒂細部 · 虛線為移動方向</p>
    </div>"""

# lat, lng, title, meta, label, kind (main|core|spot)
MARKERS = [
    (45.4642, 9.1900, "米蘭 Milano", "Day 1 落地 · Day 15–17 回程", "8", "main"),
    (45.4342, 12.3388, "威尼斯 Venezia", "Day 1–3 · 水都與外島", "1", "main"),
    (45.5275, 13.5685, "皮蘭 Piran", "Day 3 · 亞得里亞海懸崖小鎮", "2", "main"),
    (45.7817, 14.2039, "波斯托伊納洞窟", "Day 4 · Postojna Cave", "", "spot"),
    (46.0511, 14.5061, "盧比安納 Ljubljana", "Day 4 · 斯洛維尼亞首都", "3", "main"),
    (46.3637, 14.0936, "布萊德湖 Bled", "Day 5 · 湖心島與城堡", "4", "main"),
    (46.6186, 12.3025, "三峰 Tre Cime", "Day 6 · 多洛米蒂進山", "5", "core"),
    (47.2692, 11.4041, "因斯布魯克 Innsbruck", "Day 7 · 北鏈越境", "6", "main"),
    (46.5736, 11.6710, "奧蒂塞伊 Ortisei", "Day 8 · 加爾代納山谷", "", "spot"),
    (46.5270, 11.7620, "塞拉山組 Sella", "Day 9 · 環山纜車", "", "spot"),
    (46.5167, 11.7500, "薩索隆戈 Sassolungo", "Day 10", "", "spot"),
    (46.5575, 11.7133, "聖克里斯蒂娜", "Day 11 · Monte Pana", "", "spot"),
    (46.4094, 11.5753, "卡雷扎湖 Carezza", "Day 12 · 彩虹湖", "", "spot"),
    (46.5544, 11.7578, "塞爾瓦 Selva", "Day 13 · Val Gardena", "", "spot"),
    (46.6595, 11.7180, "富內斯 Funes", "Day 14 · 爆走日", "", "spot"),
    (45.4384, 10.9916, "維羅納 Verona", "Day 15 · 還車前轉程", "7", "main"),
]

ROUTE = [
    [45.4642, 9.1900],
    [45.4342, 12.3388],
    [45.5275, 13.5685],
    [46.0511, 14.5061],
    [46.3637, 14.0936],
    [46.6186, 12.3025],
    [47.2692, 11.4041],
    [46.5544, 11.7578],
    [45.4384, 10.9916],
    [45.4642, 9.1900],
]

MAP_SCRIPT = f"""
<script>
(function(){{
  var el=document.getElementById('trip-map');
  if(!el||typeof L==='undefined')return;
  var map=L.map(el,{{scrollWheelZoom:false,attributionControl:true}}).setView([46.35,11.85],7);
  L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png',{{
    attribution:'&copy; OpenStreetMap &copy; CARTO',
    subdomains:'abcd',
    maxZoom:19
  }}).addTo(map);
  var markers={json.dumps(MARKERS, ensure_ascii=False)};
  var bounds=L.latLngBounds();
  function pin(kind,label){{
    var cls='trip-pin trip-pin--'+kind;
    var inner=label?'<span class="trip-pin__label">'+label+'</span>':'<span class="trip-pin__label">·</span>';
    return L.divIcon({{
      className:'trip-pin-wrap',
      html:'<span class="'+cls+'">'+inner+'</span>',
      iconSize:kind==='core'?[34,34]:kind==='spot'?[26,26]:[30,30],
      iconAnchor:kind==='core'?[17,34]:kind==='spot'?[13,26]:[15,30],
      popupAnchor:[0,-32]
    }});
  }}
  markers.forEach(function(m){{
    var lat=m[0],lng=m[1],title=m[2],meta=m[3],label=m[4],kind=m[5];
    L.marker([lat,lng],{{icon:pin(kind,label)}})
      .addTo(map)
      .bindPopup('<strong>'+title+'</strong><em>'+meta+'</em>');
    bounds.extend([lat,lng]);
  }});
  L.polyline({json.dumps(ROUTE)},{{
    color:'#D45A35',
    weight:2.5,
    opacity:0.55,
    dashArray:'8 10',
    lineJoin:'round'
  }}).addTo(map);
  map.fitBounds(bounds,{{padding:[36,36]}});
  if(window.matchMedia('(min-width:720px)').matches){{map.zoomOut(0.5);}}
  map.on('click',function(){{map.scrollWheelZoom.enable();}});
  map.on('mouseout',function(){{map.scrollWheelZoom.disable();}});
}})();
</script>"""


def inject_leaflet_assets(html: str) -> str:
    if "leaflet@1.9.4/dist/leaflet.css" not in html:
        html = html.replace(
            '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC',
            LEAFLET_CSS + "\n" + '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC',
            1,
        )
    script_block = LEAFLET_JS + "\n" + MAP_SCRIPT
    if "leaflet@1.9.4/dist/leaflet.js" not in html:
        html = html.replace("</body>", script_block + "\n</body>", 1)
    else:
        html = re.sub(
            r'<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"[^>]*></script>\s*<script>\s*\(function\(\)\{\s*var el=document.getElementById\(\'trip-map\'\).*?</script>',
            script_block.strip(),
            html,
            count=1,
            flags=re.DOTALL,
        )
    return html


def inject_map_html(html: str) -> str:
    if 'id="trip-map"' in html:
        html = re.sub(
            r'    <div class="intro__map reveal">.*?</p>\n    </div>',
            MAP_BLOCK.strip(),
            html,
            count=1,
            flags=re.DOTALL,
        )
        return html
    needle = "    </div>\n  </div>\n</section>\n\n<nav class=\"daynav\""
    if needle not in html:
        raise RuntimeError("map insertion point not found")
    return html.replace(
        needle,
        "    </div>\n\n" + MAP_BLOCK + "\n  </div>\n</section>\n\n<nav class=\"daynav\"",
        1,
    )


def main() -> None:
    for path in FILES:
        html = path.read_text(encoding="utf-8")
        html = inject_map_html(html)
        html = inject_leaflet_assets(html)
        path.write_text(html, encoding="utf-8")
        print(f"Patched trip map in {path.name}")


if __name__ == "__main__":
    main()
