#!/usr/bin/env python3
"""Build index.html (English) and ru/index.html (Russian) from _index.html.

_index.html is the source and holds both languages.  Each published page gets
its own language only (see _strip_lang.py); the Russian page also gets its own
title, description and canonical URL.  Never edit index.html or ru/index.html
by hand.  Run after every edit of _index.html:  python3 _build_ru.py
(The leading underscore keeps GitHub Pages from publishing the source and this script.)
"""
from pathlib import Path

from _strip_lang import strip_lang

root = Path(__file__).parent
html = (root / "_index.html").read_text(encoding="utf-8")

(root / "index.html").write_text(strip_lang(html, drop="ru"), encoding="utf-8")
print("index.html updated")

swaps = [
    ('<html lang="en" data-lang="en">', '<html lang="ru" data-lang="ru">'),
    ('<title>Daniil Glushko — Russia–Asia business consultant</title>',
     '<title>Даниил Глушко — выход на рынки Азии и экспорт на Филиппины</title>'),
    ('<meta name="description" content="I help Russian companies enter Hong Kong, the Philippines and the Gulf, and Asian partners work in Russia. Partners, negotiations, export, through to the first shipment.">',
     '<meta name="description" content="Помогаю российским компаниям выйти на рынки Гонконга, Филиппин и Персидского залива: партнёры, переговоры, госорганы, экспорт. Сопровождаю до первой поставки.">'),
    ('<meta property="og:url" content="https://glushko.works/">',
     '<meta property="og:url" content="https://glushko.works/ru/">'),
    ('<meta property="og:title" content="Daniil Glushko — Russian companies in Asia. Asian partners in Russia.">',
     '<meta property="og:title" content="Даниил Глушко — российские компании в Азии, азиатские партнёры в России">'),
    ('<meta property="og:description" content="Negotiations, partners, government relations and follow-through until a deal becomes a working project. Moscow, Hong Kong, Manila, Bahrain.">',
     '<meta property="og:description" content="Переговоры, партнёры, работа с госорганами и сопровождение, пока сделка не станет работающим проектом. Москва, Гонконг, Манила, Бахрейн.">'),
    ('<meta property="og:locale" content="en_US">', '<meta property="og:locale" content="ru_RU">'),
    ('<link rel="canonical" href="https://glushko.works/">',
     '<link rel="canonical" href="https://glushko.works/ru/">'),
    ('<img src="/images/daniil-glushko.jpg" alt="Daniil Glushko (Даниил Глушко), business consultant"', '<img src="/images/daniil-glushko.jpg" alt="Даниил Глушко (Daniil Glushko), бизнес-консультант"'),
    # the Russian page needs the Cyrillic font files first
    ('<link rel="preload" href="/fonts/cormorant-garamond-normal-latin-7.woff2"',
     '<link rel="preload" href="/fonts/cormorant-garamond-normal-cyrillic-5.woff2"'),
    ('<link rel="preload" href="/fonts/golos-text-normal-latin-11.woff2"',
     '<link rel="preload" href="/fonts/golos-text-normal-cyrillic-9.woff2"'),
]

swaps += [
    ('href="/about/"', 'href="/ru/about/"'),
    ('href="/press/"', 'href="/ru/press/"'),
]

for old, new in swaps:
    if html.count(old) != 1 and not old.startswith('href='):
        raise SystemExit(f"_build_ru.py: expected exactly one match for:\n  {old}\nUpdate the swaps list.")
    html = html.replace(old, new)

(root / "ru").mkdir(exist_ok=True)
(root / "ru" / "index.html").write_text(strip_lang(html, drop="en"), encoding="utf-8")
print("ru/index.html updated")
