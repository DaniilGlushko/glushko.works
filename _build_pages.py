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
header, _ = between(src, '<header class="hdr" id="hdr">', "</header>")
footer, _ = between(src, "<footer>", "</footer>")

# nav links on sub-pages point back to the home page sections
header = (header.replace('href="#top"', 'href="/"')
          .replace('href="#', 'href="/#'))

# Russian sub-pages link to the Russian home page and sub-pages
def to_ru(fragment):
    return (fragment.replace('href="/#', 'href="/ru/#').replace('href="/"', 'href="/ru/"')
            .replace('href="/press/"', 'href="/ru/press/"').replace('href="/about/"', 'href="/ru/about/"'))


# Bio and career for /about/. Kept here (not on the home page) so the about page
# carries the full text for name searches.
BIO = [
    '<span lang="en">Every project I\'ve run had two sides that did not speak the same language: a state corporation and a university, an agency and an international federation, a Russian producer and an Asian regulator. My work is to be the one person both sides trust, and to keep the deal moving after the handshake.</span><span lang="ru">В каждом моём проекте были две стороны, которые говорили на разных языках: госкорпорация и университет, агентство и международная федерация, российский производитель и азиатский регулятор. Моя работа — быть человеком, которому доверяют обе стороны, и двигать сделку дальше после рукопожатия.</span>',
    '<span lang="en">I prepare the ground before a meeting, sit at the table during it, and take ownership of what was agreed afterwards: documents, approvals, partners, first deliveries. Companies work with me when they need someone on the other side of the border who is accountable for the result, not the process.</span><span lang="ru">Я готовлю почву до встречи, сижу за столом во время неё и отвечаю за договорённости после: документы, согласования, партнёры, первые поставки. Со мной работают, когда по ту сторону границы нужен человек, который отвечает за результат, а не за процесс.</span>',
    '<span lang="en">Moscow is home. Hong Kong is where Russian–Asian trade gets structured. Manila is where I\'ve spent the past few years building relationships in business, pharma and government. Bahrain is my door to the Gulf.</span><span lang="ru">Москва — дом. Гонконг — место, где структурируется торговля между Россией и Азией. Манила — город, где последние годы я строю отношения в бизнесе, фармацевтике и государственных структурах. Бахрейн — моя дверь в страны Залива.</span>',
]
CAREER = [
    ('2026 —', '<span lang="en">Pork and pet-food exports to the Philippines, Talina Group</span><span lang="ru">Экспорт свинины и кормов на Филиппины, ГК «Талина»</span>',
     '<span lang="en">Representing a vertically integrated Russian agro-holding in the Philippines: JV partner search for local processing and distribution; engagement with the Department of Agriculture, the Board of Investments and PEZA; deal structuring around MAV quotas and a Hong Kong trading company.</span><span lang="ru">Доверенное лицо вертикально интегрированного агрохолдинга в переговорах с филиппинскими партнёрами: поиск партнёра для СП по локальной переработке и дистрибуции, работа с Министерством сельского хозяйства, Board of Investments и PEZA, структурирование сделки с учётом квот MAV и торговой компании в Гонконге.</span>'),
    ('2026 —', '<span lang="en">Pharma track and trace, Medical Value Chain</span><span lang="ru">Прослеживаемость лекарств, Medical Value Chain</span>',
     '<span lang="en">Introducing a blockchain track-and-trace platform to the Philippine pharmaceutical sector and extending it to halal supply chains with local partners.</span><span lang="ru">Вывод блокчейн-платформы track &amp; trace на фармацевтический рынок Филиппин и расширение её на халяльные цепочки поставок с местными партнёрами.</span>'),
    ('2022 — 2026', '<span lang="en">Head of Department, Rosatom Corporate Academy</span><span lang="ru">Руководитель отдела, Корпоративная Академия Росатома</span>',
     '<span lang="en">Ran the Academy\'s talent and partnership portfolio: a network of 10+ universities and research centers (MIPT, MEPhI, Sirius), a Master\'s program in applied robotics built from scratch, the annual School of Fundamental Physics and Mathematics, the national AtomSkills championship and industry conferences with 8,000+ participants. Secured approval for USD 3.6M+ in investment projects.</span><span lang="ru">Руководил портфелем программ Академии по талантам и партнёрствам: сеть из 10+ университетов и научных центров (МФТИ, НИЯУ МИФИ, «Сириус»), магистратура по прикладной робототехнике с нуля, ежегодная Школа по фундаментальной физике и математике, чемпионат AtomSkills и отраслевые конференции на 8 000+ участников. Защитил инвестиционные проекты на 300+ млн ₽.</span>'),
    ('2021 — 2022', '<span lang="en">Head of Projects, HSE University</span><span lang="ru">Руководитель проектов, НИУ ВШЭ</span>',
     '<span lang="en">Led a 15-person project team; introduced Agile and OKRs, cutting time-to-market by 30%. Relaunched the university brand, which placed in the national RAEX ranking.</span><span lang="ru">Руководил проектной командой из 15 человек; внедрил Agile и OKR, сократив срок вывода проектов на 30%. Перезапустил бренд университета, призовое место в рейтинге RAEX.</span>'),
    ('2019 — 2021', '<span lang="en">Independent strategy consultant</span><span lang="ru">Независимый консультант по стратегии</span>',
     '<span lang="en">Advised business owners on strategy and saw it through: a social media strategy that grew a national sports brand\'s reach 3.5x; a TV commercial for Channel One, from concept to air.</span><span lang="ru">Консультировал собственников бизнеса по стратегии и доводил её до результата: SMM-стратегия, увеличившая охват национального спортивного бренда в 3,5 раза; рекламный ролик для Первого канала от идеи до эфира.</span>'),
    ('2016 — 2019', '<span lang="en">FIFA World Cup 2018 and the Children of Asia Games</span><span lang="ru">ЧМ-2018 и Игры «Дети Азии»</span>',
     '<span lang="en">International campaigns for the FIFA World Cup 2018 and Football for Friendship across 12 countries (5M+ reach) at AGT Communications; coordinated 15 Asian National Olympic Committees for the first Winter Children of Asia Games.</span><span lang="ru">Международные кампании FIFA World Cup 2018 и «Футбол для дружбы» в 12 странах (охват 5+ млн) в агентстве АГТ; координировал 15 национальных олимпийских комитетов Азии для первых зимних Игр «Дети Азии».</span>'),
]
bio = "\n".join(f"<p>{p}</p>" for p in BIO)
cases = '<div class="tl">\n' + "\n".join(
    f'  <div class="tl-item"><span class="when">{w}</span><h3>{h}</h3><p>{p}</p></div>' for w, h, p in CAREER) + "\n</div>"

EXTRA_CSS = """
<style>
.page{padding:clamp(48px,6vw,88px) 0 clamp(72px,8vw,120px)}
.page h1{font-size:clamp(44px,6vw,88px);letter-spacing:-.025em;max-width:18ch}
.page .sub{font-size:clamp(18px,1.45vw,21px);line-height:1.5;color:var(--ink-2);max-width:60ch;margin-top:22px}
.page .grid{display:grid;grid-template-columns:200px 1fr;gap:56px;align-items:start;margin-top:56px}
.page .grid img{width:200px;height:auto;aspect-ratio:4/5;object-fit:cover;filter:saturate(.72) contrast(1.03)}
.page .bio p{font-size:clamp(17px,1.2vw,19px);color:var(--ink-2);max-width:62ch}
.page .bio p+p{margin-top:16px}
.page h2.title{margin:clamp(64px,7vw,104px) 0 28px;font-size:clamp(34px,3.6vw,56px)}
.page .links{display:flex;flex-wrap:wrap;gap:10px;margin-top:28px}
.page .links a{font-size:14px;text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:8px 16px;transition:border-color .2s,color .2s}
.page .links a:hover{border-color:var(--gold-ink);color:var(--gold-ink)}
.page .btn{margin-top:48px}
.photos{display:grid;grid-template-columns:repeat(12,1fr);gap:20px;align-items:start}
.photos figure{margin:0;grid-column:span 3}
.photos figure:first-child{grid-column:span 6}
.photos img{width:100%;height:auto;display:block;filter:saturate(.85)}
.photos figcaption{margin-top:10px;font-size:13px;color:var(--ink-3);line-height:1.4}
@media (max-width:820px){.photos figure,.photos figure:first-child{grid-column:span 6}}
.tl{border-top:1px solid var(--ink)}
.tl-item{display:grid;grid-template-columns:repeat(12,1fr);gap:8px 24px;padding:24px 0;border-bottom:1px solid var(--line);align-items:baseline}
.tl-item .when{grid-column:1/3;font-family:var(--mono);font-size:12px;color:var(--ink-3);letter-spacing:.06em}
.tl-item h3{grid-column:3/13;font-size:clamp(22px,1.8vw,28px)}
.tl-item p,.tl-item .src{grid-column:3/11;font-size:15px;color:var(--ink-2)}
.tl-item h3 a{text-decoration:none;border-bottom:1px solid var(--line);transition:border-color .2s,color .2s}
.tl-item h3 a:hover{border-color:var(--gold-ink);color:var(--gold-ink)}
@media (max-width:820px){
  .page .grid{grid-template-columns:1fr;gap:28px}
  .page .grid img{width:140px}
  .tl-item .when,.tl-item h3,.tl-item p,.tl-item .src{grid-column:1/13}
}
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
        "https://tenchat.ru/glushko_daniil",
    ],
}


def head(lang, page, title, desc):
    en_url = f"https://glushko.works/{page}/"
    ru_url = f"https://glushko.works/ru/{page}/"
    canon = en_url if lang == "en" else ru_url
    if page == "about":
        person = dict(PERSON)
        person["image"] = [PERSON["image"]] + PHOTO_URLS
        ld = {"@context": "https://schema.org", "@type": "ProfilePage", "mainEntity": person, "url": canon,
              "image": [{"@type": "ImageObject", "contentUrl": u, "name": (en if lang == "en" else ru)}
                        for (f, w, h, en, ru), u in zip(PHOTOS, PHOTO_URLS)]}
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
{style}
{EXTRA_CSS}
</head>
<body>
{header if lang == "en" else to_ru(header)}
"""


PHOTOS = [
    ("daniil-glushko-rosatom.jpg", 1600, 900,
     "Daniil Glushko at a Rosatom Corporate Academy round table, Moscow",
     "Даниил Глушко на круглом столе Корпоративной академии Росатома, Москва"),
    ("daniil-glushko-shanghai.jpg", 1200, 1600,
     "Daniil Glushko in Shanghai, Pudong",
     "Даниил Глушко в Шанхае, Пудун"),
    ("daniil-glushko-portrait-studio.jpg", 724, 1086,
     "Daniil Glushko, studio portrait",
     "Даниил Глушко, студийный портрет"),
    ("daniil-glushko-trail-run.jpg", 1066, 1600,
     "Daniil Glushko at a 100 km trail race",
     "Даниил Глушко на трейловом забеге на 100 км"),
]

def photos_html():
    figs = []
    for f, w, h, en, ru in PHOTOS:
        figs.append(f"""      <figure>
        <img src="/images/{f}" alt="{en} / {ru}" width="{w}" height="{h}" loading="lazy" decoding="async">
        <figcaption><span lang="en">{en}</span><span lang="ru">{ru}</span></figcaption>
      </figure>""")
    return "\n".join(figs)

PHOTO_URLS = [f"https://glushko.works/images/{f}" for f, *_ in PHOTOS]

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
          <a href="https://tenchat.ru/glushko_daniil" rel="me">TenChat</a>
          <a href="https://roscongress.ru/speakers/glushko-daniil/"><span lang="en">Roscongress speaker profile</span><span lang="ru">Профиль спикера на Росконгрессе</span></a>
          <a href="/press/" data-ru="/ru/press/"><span lang="en">Publications and talks</span><span lang="ru">Публикации и выступления</span></a>
        </div>
      </div>
    </div>
    <h2 class="title"><span lang="en">In the field</span><span lang="ru">В работе и в дороге</span></h2>
    <div class="photos">
{photos_html()}
    </div>
    <h2 class="title"><span lang="en">Career</span><span lang="ru">Карьера</span></h2>
    {cases}
    <a class="btn" href="/#contact"><span lang="en">Tell me about your deal</span><span lang="ru">Рассказать о задаче</span></a>
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
        items.append(f"""      <div class="tl-item">
        <span class="when">{when}</span>
        <h3><a href="{url}" rel="noopener"><span lang="en">{en}</span><span lang="ru">{ru}</span></a></h3>
        <span class="src"><span lang="en">{src_en}</span><span lang="ru">{src_ru}</span></span>
      </div>""")
    return f"""
<main class="page press">
  <div class="wrap">
    <h1><span lang="en">Daniil Glushko: publications and talks</span><span lang="ru">Даниил Глушко: публикации и выступления</span></h1>
    <p class="sub"><span lang="en">Where I have spoken or been quoted: forums, industry media, educational programmes.</span><span lang="ru">Где я выступал или давал комментарии: форумы, отраслевые медиа, образовательные программы.</span></p>
    <div class="tl" style="margin-top:48px">
{chr(10).join(items)}
    </div>
    <h2 class="title"><span lang="en">Daniil Glushko online</span><span lang="ru">Даниил Глушко в сети</span></h2>
    <div class="links">
      <a href="https://www.linkedin.com/in/ddaniilglushko" rel="me">LinkedIn</a>
      <a href="https://tenchat.ru/glushko_daniil" rel="me">TenChat</a>
      <a href="https://t.me/finchmadeit" rel="me">Telegram</a>
      <a href="https://roscongress.ru/speakers/glushko-daniil/"><span lang="en">Roscongress speaker profile</span><span lang="ru">Профиль спикера на Росконгрессе</span></a>
    </div>
    <a class="btn" href="/about/" data-ru="/ru/about/"><span lang="en">About Daniil Glushko</span><span lang="ru">О Данииле Глушко</span></a>
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
        doc = (head(lang, page, title, desc) + body + "\n" + (footer if lang == "en" else to_ru(footer)) + "\n"
               + SCRIPT.replace("PAGE", repr(page)) + "</body>\n</html>\n")
        out = root / (page if lang == "en" else f"ru/{page}") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(doc, encoding="utf-8")
        print("wrote", out.relative_to(root))
