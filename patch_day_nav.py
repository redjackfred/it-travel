#!/usr/bin/env python3
"""Add day IDs, navigation bar, and scroll-spy script to handbook HTML."""

import re
from pathlib import Path

ROOT = Path(__file__).parent
FILES = [ROOT / "多洛米蒂旅遊手冊.html", ROOT / "index.html"]

DAYS = [
    (0, "6/29", "台北出發"),
    (1, "6/30", "米蘭→威尼斯"),
    (2, "7/1", "跳島"),
    (3, "7/2", "皮蘭"),
    (4, "7/3", "盧比安納"),
    (5, "7/4", "布萊德湖"),
    (6, "7/5", "進山"),
    (7, "7/6", "因斯布魯克"),
    (8, "7/7", "Ortisei"),
    (9, "7/8", "Sella"),
    (10, "7/9", "Sassolungo"),
    (11, "7/10", "S.Cristina"),
    (12, "7/11", "Carezza"),
    (13, "7/12", "Selva"),
    (14, "7/13", "Funes"),
    (15, "7/14", "還車"),
    (16, "7/15", "米蘭"),
    (17, "7/16", "回程"),
]

CHAPTERS = [
    ("01", "LAGOON", range(0, 3)),
    ("02", "EMERALD", range(3, 6)),
    ("03", "HEART", range(6, 15)),
    ("04", "FINALE", range(15, 18)),
]

DAY_LABELS_JS = ", ".join(f'"{label}"' for _, _, label in DAYS)

ARTICLE_PAT = re.compile(
    r'<article class="day reveal"(?: id="day-\d+")?>\s*'
    r'<div class="day__rail"><div class="day__num serif">(\d+)'
)

NAV_MARKER = '<!-- CH1 VENICE -->'

DAYNAV_JS = f"""
    /* day navigation */
    (function(){{
      var nav=document.getElementById('daynav');
      if(!nav)return;
      var links=nav.querySelectorAll('[data-day]');
      var mobileDay=nav.querySelector('.daynav__mobile-day');
      var mobileLabel=nav.querySelector('.daynav__mobile-label');
      var labels=[{DAY_LABELS_JS}];
      var sections=[];
      links.forEach(function(a){{
        var n=parseInt(a.getAttribute('data-day'),10);
        var el=document.getElementById('day-'+n);
        if(el)sections.push({{n:n,el:el,link:a}});
      }});
      function setActive(n){{
        links.forEach(function(a){{
          a.classList.toggle('is-active',parseInt(a.getAttribute('data-day'),10)===n);
        }});
        if(mobileDay)mobileDay.textContent='Day '+n;
        if(mobileLabel&&labels[n])mobileLabel.textContent=labels[n];
        var active=nav.querySelector('.daynav__pill.is-active,.daynav__dot-link.is-active');
        if(active){{
          if(active.closest('.daynav__mobile-track')){{
            active.scrollIntoView({{inline:'center',block:'nearest',behavior:'smooth'}});
          }}else if(active.closest('.daynav__desktop')){{
            active.scrollIntoView({{block:'nearest',behavior:'smooth'}});
          }}
        }}
      }}
      if('IntersectionObserver' in window&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches){{
        var ratios={{}};
        var io=new IntersectionObserver(function(entries){{
          entries.forEach(function(x){{
            ratios[x.target.id]=x.intersectionRatio;
          }});
          var best=null,bestR=0;
          sections.forEach(function(s){{
            var r=ratios['day-'+s.n]||0;
            if(r>bestR){{bestR=r;best=s.n;}}
          }});
          if(bestR>0)setActive(best);
        }},{{rootMargin:'-20% 0px -55% 0px',threshold:[0,.15,.35,.55,.75]}});
        sections.forEach(function(s){{io.observe(s.el);}});
      }}
      links.forEach(function(a){{
        a.addEventListener('click',function(e){{
          var n=parseInt(a.getAttribute('data-day'),10);
          var el=document.getElementById('day-'+n);
          if(!el)return;
          e.preventDefault();
          el.scrollIntoView({{behavior:'smooth',block:'start'}});
          setActive(n);
        }});
      }});
      if(sections.length)setActive(sections[0].n);
    }})();
"""


def build_nav_html() -> str:
    mobile_links = "\n".join(
        f'        <a class="daynav__dot-link{" is-active" if n == 0 else ""}" href="#day-{n}" data-day="{n}">{n}</a>'
        for n, _, _ in DAYS
    )

    groups = []
    day_map = {n: (date, label) for n, date, label in DAYS}
    for ch_num, ch_tag, day_range in CHAPTERS:
        pills = []
        for n in day_range:
            date, label = day_map[n]
            active = ' is-active' if n == 0 else ""
            pills.append(
                f'<a class="daynav__pill{active}" href="#day-{n}" data-day="{n}">'
                f'<span class="daynav__pill-n">{n}</span>'
                f'<span class="daynav__pill-t"><em>{date}</em>{label}</span></a>'
            )
        groups.append(
            f'        <div class="daynav__group">\n'
            f'          <span class="daynav__group-label">CH.{ch_num} · {ch_tag}</span>\n'
            f'          <div class="daynav__pills">{"".join(pills)}</div>\n'
            f'        </div>'
        )

    return f"""<nav class="daynav" id="daynav" aria-label="行程天數導覽">
  <div class="daynav__mobile">
    <div class="daynav__mobile-head">
      <span class="daynav__mobile-day mono">Day 0</span>
      <span class="daynav__mobile-label">{DAYS[0][2]}</span>
    </div>
    <div class="daynav__mobile-track" role="tablist">
{mobile_links}
    </div>
  </div>
  <div class="daynav__desktop">
    <div class="daynav__inner">
      <span class="daynav__title">行程</span>
      <div class="daynav__groups">
{chr(10).join(groups)}
      </div>
    </div>
  </div>
</nav>
"""


def add_day_ids(html: str) -> str:
    def repl(m: re.Match[str]) -> str:
        return f'<article class="day reveal" id="day-{m.group(1)}">\n      <div class="day__rail"><div class="day__num serif">{m.group(1)}'

    return ARTICLE_PAT.sub(repl, html)


def inject_nav(html: str) -> str:
    nav = build_nav_html()
    if 'id="daynav"' in html:
        html = re.sub(r'<nav class="daynav" id="daynav".*?</nav>\s*', nav + "\n", html, count=1, flags=re.DOTALL)
    elif NAV_MARKER in html:
        html = html.replace(NAV_MARKER, nav + "\n" + NAV_MARKER, 1)
    else:
        raise RuntimeError("nav injection point not found")
    return html


SCRIPT_PAT = re.compile(r"<script>\s*\(function\(\)\{.*?</script>", re.DOTALL)


def rewrite_script(html: str) -> str:
    script = (
        "<script>\n"
        "  (function(){\n"
        "    document.querySelectorAll('.cell img').forEach(function(img){\n"
        "      img.addEventListener('error',function(){img.style.display='none';});\n"
        "    });\n"
        "    var els=document.querySelectorAll('.reveal');\n"
        "    if('IntersectionObserver' in window&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches){\n"
        "      var io=new IntersectionObserver(function(en){en.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}});},{threshold:.1});\n"
        "      els.forEach(function(e){io.observe(e);});\n"
        "    }else{\n"
        "      els.forEach(function(e){e.classList.add('in');});\n"
        "    }\n"
        + DAYNAV_JS
        + "  })();\n"
        "</script>"
    )
    if not SCRIPT_PAT.search(html):
        raise RuntimeError("script block not found")
    return SCRIPT_PAT.sub(script, html, count=1)


def inject_js(html: str) -> str:
    return rewrite_script(html)


def main() -> None:
    for path in FILES:
        html = path.read_text(encoding="utf-8")
        html = add_day_ids(html)
        html = inject_nav(html)
        html = inject_js(html)
        path.write_text(html, encoding="utf-8")
        print(f"Patched day nav in {path.name}")


if __name__ == "__main__":
    main()
