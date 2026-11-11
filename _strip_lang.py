#!/usr/bin/env python3
"""Leave only one language in a built page.

The source (_index.html and the fragments in _build_pages.py) keeps both
languages side by side:  <span lang="en">…</span><span lang="ru">…</span>.
The other language used to stay in the published HTML, hidden by CSS.  That
made / and /ru/ (and each pair of sub-pages) near-identical documents, and
Yandex kept one page of each pair and dropped the other from its index.

strip_lang() cuts every element marked with the other language out of the
page, so each published page carries the text of its own language only.
(The leading underscore keeps GitHub Pages from publishing this script.)
"""
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class _Finder(HTMLParser):
    """Collects the character ranges of elements whose lang attribute is `drop`."""

    def __init__(self, raw, drop):
        super().__init__(convert_charrefs=False)
        self.raw, self.drop = raw, drop
        self.line_starts = [0] + [i + 1 for i, ch in enumerate(raw) if ch == "\n"]
        self.ranges = []
        self.open = None  # [tag, start offset, nesting depth of the same tag]

    def _offset(self):
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def _start(self, tag, attrs, self_closing):
        start = self._offset()
        end = start + len(self.get_starttag_text())
        if self.open:
            if tag == self.open[0] and not self_closing:
                self.open[2] += 1
            return
        if tag == "html" or dict(attrs).get("lang") != self.drop:
            return
        if self_closing:
            self.ranges.append((start, end))
        else:
            self.open = [tag, start, 1]

    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs, tag in VOID)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs, True)

    def handle_endtag(self, tag):
        if self.open and tag == self.open[0]:
            self.open[2] -= 1
            if self.open[2] == 0:
                start = self._offset()
                self.ranges.append((self.open[1], self.raw.index(">", start) + 1))
                self.open = None


def _ranges(html, drop):
    finder = _Finder(html, drop)
    finder.feed(html)
    finder.close()
    if finder.open:
        raise SystemExit(f"_strip_lang.py: <{finder.open[0]} lang=\"{drop}\"> is never closed")
    return finder.ranges


def strip_lang(html, drop):
    """Return html without the elements marked lang="<drop>" ("en" or "ru")."""
    out, pos = [], 0
    for start, end in _ranges(html, drop):
        out.append(html[pos:start])
        pos = end
    out.append(html[pos:])
    result = "".join(out)
    if _ranges(result, drop):
        raise SystemExit(f"_strip_lang.py: lang=\"{drop}\" elements are still in the page")
    return result
