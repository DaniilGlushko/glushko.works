#!/usr/bin/env python3
"""Build ru/index.html from index.html.

index.html holds both languages; the Russian page is the same file with
Russian shown by default and its own title, description and canonical URL.
Run after every edit of index.html:  python3 _build_ru.py
(The leading underscore keeps GitHub Pages from publishing this script.)
"""
from pathlib import Path

root = Path(__file__).parent
html = (root / "index.html").read_text(encoding="utf-8")

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
    ('<img src="/images/portrait.jpg" alt="Daniil Glushko"', '<img src="/images/portrait.jpg" alt="Даниил Глушко"'),
]

for old, new in swaps:
    if html.count(old) != 1:
        raise SystemExit(f"_build_ru.py: expected exactly one match for:\n  {old}\nUpdate the swaps list.")
    html = html.replace(old, new)

(root / "ru").mkdir(exist_ok=True)
(root / "ru" / "index.html").write_text(html, encoding="utf-8")
print("ru/index.html updated")
