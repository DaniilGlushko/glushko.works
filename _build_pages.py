#!/usr/bin/env python3
"""Build /about/ and /press/ (EN) and /ru/about/, /ru/press/ (RU) from index.html.

The sub-pages reuse the <style> block, header and footer of index.html, so the
look stays in sync.  Bio paragraphs and the career list are taken from the
"about" and "work" sections of index.html, so edit them there.
Run after every edit of index.html:  python3 _build_ru.py && python3 _build_pages.py
"""
import json
import re
from pathlib import Path

root = Path(__file__).parent
src = (root / "index.html").read_text(encoding="utf-8")


def between(text, start, end, start_from=0):
    i = text.index(start, start_from)
    j = text.index(end, i)
    return text[i:j + len(end)], j


style, _ = between(src, "<style>", "</style>")
header, _ = between(src, '<header class="bar">', "</header>")
footer, _ = between(src, '<footer class="wrap">', "</footer>")

# nav links on sub-pages point back to the home page sections
header = (header.replace('href="#"', 'href="/"')
          .replace('href="#about"', 'href="/#about"').replace('href="#services"', 'href="/#services"')
          .replace('href="#how"', 'href="/#how"').replace('href="#work"', 'href="/#work"')
          .replace('href="#contact"', 'href="/#contact"')
          .replace('<header class="bar">', '<header class="bar solid">'))

about_sec, _ = between(src, '<section id="about"', "</section>")
bio = "\n".join(re.findall(r"<p><span lang=\"en\">.*?</p>", about_sec, re.S)[:3])

work_sec, _ = between(src, '<section id="work"', "</section>")
cases = work_sec[work_sec.index('<div class="cases">'):work_sec.rindex("</div>")]
cases = cases[:cases.rindex("</div>") + len("</div>")]  # keep .cases closed, drop .wrap closing

EXTRA_CSS = """
<style>
.bar.solid{position:static;background:#0E3B4A}
.page{padding:72px 0 96px}
.page h1{font-size:clamp(38px,5vw,62px);font-weight:400;max-width:20ch}
.page .sub{font-size:clamp(18px,2vw,22px);color:var(--ink-2);max-width:60ch;margin-top:14px}
.page .grid{display:grid;grid-template-columns:300px 1fr;gap:56px;align-items:start;margin-top:48px}
.page .grid img{width:100%;height:auto;border-radius:4px;box-shadow:0 20px 50px rgba(0,0,0,.18)}
.page .bio p{margin-top:18px;max-width:64ch}
.page .bio p:first-child{margin-top:0}
.page h2.title{margin-top:72px}
.page .links{display:flex;flex-wrap:wrap;gap:12px 24px;margin-top:24px}
.page .links a{text-decoration:none;border-bottom:1px solid var(--sun)}
.page .cta{display:inline-block;margin-top:40px;background:#0E3B4A;color:#fff;text-decoration:none;font-weight:600;padding:15px 30px;border-radius:999px}
.page .cta:hover{background:var(--sun);color:#15211F}
.press .case h3 a{text-decoration:none;border-bottom:1px solid var(--line)}
.press .case h3 a:hover{border-color:var(--sun)}
.press .case .src{display:block;color:var(--ink-2);font-size:14px;margin-top:4px}
@media (max-width:720px){.page .grid{grid-template-columns:1fr;gap:32px}.page .grid img{max-width:320px}}
</style>
"""

SCRIPT = """
<script>
(function(){
  var html=document.documentElement, btns=document.querySelectorAll('.lang button');
  btns.forEach(function(b){
    b.setAttribute('aria-pressed',String(b.dataset.set===html.getAttribute('data-lang')));
    b.addEventListener('click',function(){
      if(b.dataset.set!==html.getAttribute('data-lang')) location.href=b.dataset.set==='ru'?'/ru/'+PAGE+'/':'/'+PAGE+'/';
    });
  });
})();
</script>
"""

PERSON = {
    "@type": "Person",
    "@id": "https://glushko.works/#daniil",
    "name": "Daniil Glushko",
    "alternateName": ["Даниил Глушко", "Глушко Даниил", "Глушко Даниил Дмитриевич", "Даниил Дмитриевич Глушко", "Daniil Dmitrievich Glushko", "Glushko Daniil"],
    "givenName": "Daniil",
    "familyName": "Glushko",
    "url": "https://glushko.works/about/",
    "image": "https://glushko.works/images/daniil-glushko.jpg",
    "email": "mailto:daniil@glushko.works",
    "jobTitle": "Cross-border business consultant, Russia and Asia",
    "description": "Business consultant helping Russian companies enter Hong Kong, the Philippines and the Gulf, and Asian partners work in Russia. Former head of department at Rosatom Corporate Academy.",
    "knowsLanguage": ["en", "ru"],
    "sameAs": [
        "https://www.linkedin.com/in/ddaniilglushko",
        "https://t.me/finchmadeit",
        "https://roscongress.ru/speakers/glushko-daniil/",
    ],
}


def head(lang, page, title, desc):
    en_url = f"https://glushko.works/{page}/"
    ru_url = f"https://glushko.works/ru/{page}/"
    canon = en_url if lang == "en" else ru_url
    if page == "about":
        ld = {"@context": "https://schema.org", "@type": "ProfilePage", "mainEntity": PERSON, "url": canon}
    else:
        ld = {"@context": "https://schema.org", "@type": "CollectionPage",
              "about": {"@id": "https://glushko.works/#daniil"}, "name": title, "url": canon}
    return f"""<!DOCTYPE html>
<html lang="{lang}" data-lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%230E3B4A'/%3E%3Ctext x='32' y='43' text-anchor='middle' font-family='Georgia,serif' font-size='30' fill='%23D9A441'%3EDG%3C/text%3E%3C/svg%3E">
<meta property="og:type" content="profile">
<meta property="og:url" content="{canon}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://glushko.works/og.jpg">
<meta property="og:locale" content="{'en_US' if lang == 'en' else 'ru_RU'}">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="ru" href="{ru_url}">
<link rel="alternate" hreflang="x-default" href="{en_url}">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@300;400;500&family=Golos+Text:wght@400;500;600&display=swap" rel="stylesheet">
{style}
{EXTRA_CSS}
</head>
<body>
{header}
"""


ABOUT_BODY = f"""
<main class="page">
  <div class="wrap">
    <h1><span lang="en">Daniil Glushko</span><span lang="ru">Даниил Глушко</span></h1>
    <p class="sub"><span lang="en">Daniil Dmitrievich Glushko. Business consultant for Russian companies in Asia and Asian partners in Russia. Negotiations, partners, government relations. Moscow, Hong Kong, Manila, Bahrain.</span><span lang="ru">Глушко Даниил Дмитриевич. Бизнес-консультант: российские компании в Азии и азиатские партнёры в России. Переговоры, партнёры, работа с госорганами. Москва, Гонконг, Манила, Бахрейн.</span></p>
    <div class="grid">
      <img src="/images/daniil-glushko.jpg" alt="Daniil Glushko (Даниил Глушко), business consultant" width="800" height="1000" decoding="async">
      <div class="bio">
        {bio}
        <p><span lang="en">Before consulting I spent four years at Rosatom Corporate Academy, where I ran the talent and partnership portfolio: a network of universities and research centres, a Master's programme in applied robotics, the national AtomSkills championship and industry conferences with thousands of participants. Earlier I ran international campaigns around the FIFA World Cup 2018 and coordinated fifteen Asian National Olympic Committees for the Children of Asia Games.</span><span lang="ru">До консалтинга я четыре года работал в Корпоративной академии Росатома, где отвечал за программы по талантам и партнёрствам: сеть университетов и научных центров, магистратуру по прикладной робототехнике, чемпионат AtomSkills и отраслевые конференции на тысячи участников. Ещё раньше вёл международные кампании вокруг чемпионата мира по футболу 2018 и координировал пятнадцать национальных олимпийских комитетов Азии для Игр «Дети Азии».</span></p>
        <div class="links">
          <a href="https://www.linkedin.com/in/ddaniilglushko" rel="me">LinkedIn</a>
          <a href="https://t.me/finchmadeit" rel="me">Telegram</a>
          <a href="https://roscongress.ru/speakers/glushko-daniil/"><span lang="en">Roscongress speaker profile</span><span lang="ru">Профиль спикера на Росконгрессе</span></a>
          <a href="/press/" data-ru="/ru/press/"><span lang="en">Publications and talks</span><span lang="ru">Публикации и выступления</span></a>
        </div>
      </div>
    </div>
    <h2 class="title"><span lang="en">Career</span><span lang="ru">Карьера</span></h2>
    {cases}
    <a class="cta" href="/#contact"><span lang="en">Tell me about your deal</span><span lang="ru">Рассказать о задаче</span></a>
  </div>
</main>
"""

PRESS_ITEMS = [
    ("2026-11-10", "https://roscongress.ru/speakers/glushko-daniil/",
     "Speaker, International Forum on Collective Security, Moscow",
     "Спикер, Международный форум обеспечения коллективной безопасности, Москва",
     "Roscongress Foundation", "Фонд Росконгресс"),
    ("2023-06-22", "https://www.atomic-energy.ru/news/2023/06/22/136448",
     "Robotics education discussed at the AtomSkills-2023 business programme",
     "Перспективы образования в области робототехники обсудили в рамках деловой программы AtomSkills-2023",
     "Atomic Energy 2.0", "Атомная энергия 2.0"),
    ("2023-04-27", "https://siriusmag.ru/articles/1235-vkalyvat-robotov-zastavit-inzener-budusego/",
     "The engineer of the future will put robots to work",
     "Вкалывать роботов заставит инженер будущего",
     "Sirius magazine", "Журнал «Сириус»"),
    ("2023", "https://rosatom-academy.ru/media/novosti/v-universitete-sirius-zavershilas-intensivnaya-shkola-robototekhniki-pri-podderzhke-rosatoma/",
     "Intensive robotics school at Sirius University, supported by Rosatom",
     "В Университете «Сириус» завершилась интенсивная школа робототехники при поддержке Росатома",
     "Rosatom Corporate Academy", "Корпоративная академия Росатома"),
    ("2023", "https://vkvideo.ru/video-177129873_456239419",
     "Sirius: robotics school (video)", "Сириус: школа робототехники (видео)",
     "VK Video", "VK Видео"),
]


def press_body():
    items = []
    for when, url, en, ru, src_en, src_ru in PRESS_ITEMS:
        items.append(f"""      <div class="case">
        <div class="when">{when}</div>
        <div>
          <h3><a href="{url}" rel="noopener"><span lang="en">{en}</span><span lang="ru">{ru}</span></a></h3>
          <span class="src"><span lang="en">{src_en}</span><span lang="ru">{src_ru}</span></span>
        </div>
      </div>""")
    return f"""
<main class="page press">
  <div class="wrap">
    <h1><span lang="en">Daniil Glushko: publications and talks</span><span lang="ru">Даниил Глушко: публикации и выступления</span></h1>
    <p class="sub"><span lang="en">Where I have spoken or been quoted: forums, industry media, educational programmes.</span><span lang="ru">Где я выступал или давал комментарии: форумы, отраслевые медиа, образовательные программы.</span></p>
    <div class="cases" style="margin-top:48px">
{chr(10).join(items)}
    </div>
    <a class="cta" href="/about/" data-ru="/ru/about/"><span lang="en">About Daniil Glushko</span><span lang="ru">О Данииле Глушко</span></a>
  </div>
</main>
"""


PAGES = {
    "about": {
        "en": ("Daniil Glushko — business consultant, Russia and Asia",
               "Daniil Dmitrievich Glushko: cross-border business consultant. Russian companies in Hong Kong, the Philippines and the Gulf; Asian partners in Russia. Biography, career, contacts."),
        "ru": ("Даниил Дмитриевич Глушко — бизнес-консультант, Россия и Азия",
               "Глушко Даниил Дмитриевич: консультант по выходу российских компаний в Гонконг, на Филиппины и в страны Залива и по работе азиатских партнёров в России. Биография, карьера, контакты."),
        "body": ABOUT_BODY,
    },
    "press": {
        "en": ("Daniil Glushko — publications and talks",
               "Publications, interviews and talks by Daniil Glushko: Roscongress, AtomSkills, Sirius University, Rosatom Corporate Academy."),
        "ru": ("Даниил Глушко — публикации и выступления",
               "Публикации, интервью и выступления Даниила Глушко: Росконгресс, AtomSkills, Университет «Сириус», Корпоративная академия Росатома."),
        "body": press_body(),
    },
}

for page, cfg in PAGES.items():
    for lang in ("en", "ru"):
        title, desc = cfg[lang]
        body = cfg["body"]
        if lang == "ru":
            body = (body.replace('href="/press/" data-ru="/ru/press/"', 'href="/ru/press/"')
                    .replace('href="/about/" data-ru="/ru/about/"', 'href="/ru/about/"')
                    .replace('alt="Daniil Glushko (Даниил Глушко), business consultant"',
                             'alt="Даниил Глушко (Daniil Glushko), бизнес-консультант"'))
        else:
            body = body.replace(' data-ru="/ru/press/"', '').replace(' data-ru="/ru/about/"', '')
        doc = (head(lang, page, title, desc) + body + "\n" + footer + "\n"
               + SCRIPT.replace("PAGE", repr(page)) + "</body>\n</html>\n")
        out = root / (page if lang == "en" else f"ru/{page}") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(doc, encoding="utf-8")
        print("wrote", out.relative_to(root))
