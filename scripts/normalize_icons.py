"""Regenerate tight SVG icons from the bundled Font Awesome glyph outlines.
Requires fonttools and brotli. Icon attribution/license remains in assets/fontawesome/css/all.min.css.
"""
from pathlib import Path
import re
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
root = Path(__file__).resolve().parents[1]
css = (root / 'assets/fontawesome/css/all.min.css').read_text()
codes = {}
for selectors, code in re.findall(r'([^{}]+)\{--fa:"\\([0-9a-f]+)"\}', css):
    for selector in selectors.split(','):
        codes[selector.removeprefix('.fa-')] = int(code, 16)
fonts = {family: TTFont(root / f'assets/fontawesome/webfonts/{filename}.woff2')
         for family, filename in [('solid', 'fa-solid-900'), ('brands', 'fa-brands-400')]}

def svg(family, name):
    font = fonts[family]
    glyphs = font.getGlyphSet()
    glyph = glyphs[font.getBestCmap()[codes[name]]]
    bounds = BoundsPen(glyphs)
    glyph.draw(bounds)
    x0, y0, x1, y1 = bounds.bounds
    w, h = x1-x0, y1-y0
    path = SVGPathPen(glyphs)
    glyph.draw(TransformPen(path, (1, 0, 0, -1, 0, 0)))
    # Same maximum dimension, but no empty font side bearings or vertical padding.
    scale = 0.95 / max(w, h)
    return (f'<svg class="link-icon" data-icon="{family}:{name}" aria-hidden="true" focusable="false" '
            f'viewBox="{x0:g} {-y1:g} {w:g} {h:g}" style="width:{w*scale:.5f}em;height:{h*scale:.5f}em" '
            f'fill="currentColor"><path d="{path.getCommands()}"/></svg>')

p = root / 'index.html'
s = p.read_text()
s = re.sub(r'<i class="fa-(solid|brands) fa-([^\"]+)" aria-hidden="true"></i>',
           lambda m: svg(*m.groups()), s)
s = re.sub(r'<svg class="link-icon" data-icon="(solid|brands):([^\"]+)".*?</svg>',
           lambda m: svg(*m.groups()), s)
s = re.sub(r'(</svg>)<span>', r'\1<span class="link-label">', s)
s = s.replace('class="email-toggle-label"', 'class="email-toggle-label link-label"')
p.write_text(s)
print('Regenerated normalized SVGs from the existing licensed icon font.')
