"""Gera a logo vetorial do Reserva das Brisas e injeta as partes no teaser.

Uso: python tools/build_logo.py [caminho/Montserrat[wght].ttf]
  Sem a fonte, usa os contornos salvos em tools/wordmark.json.

Saídas:
  logo/reserva-das-brisas.svg           versão estática (positiva)
  logo/reserva-das-brisas-negativa.svg  para fundos escuros
  logo/reserva-das-brisas-animada.svg   com animação CSS embutida
  logo/simbolo.svg                      apenas o símbolo
  src/index.src.html -> index.html      troca {{logo:tipo:tom}} e {{basa:tom}} por SVG inline
"""
import json
import re
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent

NAVY, BLUE, LIGHT = "#163d70", "#2868b4", "#77a2d6"
LEAF, LEAF_SOFT, SKY = "#aac9f8", "#acc8e9", "#e6f1fe"

# Símbolo em 500x500, traçado sobre a logo original. Cada painel é um vidro
# do "vitral"; os vãos brancos entre eles formam a árvore.
PANELS = [
    ("n", "M0 0H278Q140 42 0 125Z"),
    ("n", "M28 140L85 108L112 165Q72 146 28 140Z"),
    ("n", "M105 97L195 57L227 245Q190 207 142 182Z"),
    ("n", "M0 158Q70 165 122 188L123 266Q52 240 0 198Z"),
    ("n", "M0 218L66 266L0 278Z"),
    ("l", "M145 205Q190 240 217 278Q178 282 145 273Z"),
    ("l", "M217 50Q250 37 280 33L290 150L225 115Z"),
    ("b", "M233 148L292 172L294 193L253 258Z"),
    ("b", "M292 0H360L395 107Q345 125 313 160Z"),
    ("b", "M383 0H500V34L415 96Z"),
    ("b", "M358 155Q440 115 500 62V170Q440 158 358 155Z"),
    ("l", "M334 177L428 185Q405 238 360 247L294 256V240Z"),
    ("l", "M464 190Q485 192 500 198V308Q440 305 375 322Q410 245 464 190Z"),
    ("b", "M294 276L375 266Q340 340 294 375Z"),
    ("n", "M0 305Q120 270 233 318L232 500H0Z"),
    ("b", "M313 398Q380 330 450 330Q480 330 500 334V500H313Z"),
]
# (cx, cy, rotação, escala, tom)
LEAVES = [
    (164, 134, 8, 1.2, "a"),
    (257, 88, -28, 0.95, "s"),
    (343, 88, 18, 1.1, "s"),
    (82, 210, -38, 1.15, "a"),
    (356, 215, -62, 1.05, "s"),
    (448, 270, 38, 1.45, "s"),
    (72, 342, -64, 1.45, "a"),
    (180, 372, 2, 1.45, "a"),
    (404, 388, -44, 1.45, "a"),
]
LEAF_PATH = "M0 -32C20 -16 20 16 0 32C-20 16 -20 -16 0 -32ZM-1 29L-5 -6L3 -1Z"

# Lettering: alturas de versal e larguras medidas na arte original.
WORDS = {
    "reserva": dict(text="RESERVA", wght=800, cap=78, base=634, width=517),
    "brisas": dict(text="DAS BRISAS", wght=700, cap=35, base=699, width=562),
}


def word_path(font_path, text, wght, cap, base, width):
    font = TTFont(font_path)
    font = instantiateVariableFont(font, {"wght": wght})
    gs, cmap = font.getGlyphSet(), font.getBestCmap()
    hmtx = font["hmtx"]
    scale = cap / font["OS/2"].sCapHeight
    names = [cmap[ord(c)] for c in text]
    # O espaço entre palavras fica mais curto para não abrir um buraco no tracking
    adv = [hmtx[n][0] * scale * (0.35 if n == "space" else 1) for n in names]
    # Espaço entra sem tracking extra; tracking distribuído entre as letras
    gaps = len(text) - 1
    natural = sum(adv[:-1]) + (hmtx[names[-1]][0] - hmtx[names[-1]][1]) * scale
    track = (width - natural) / gaps
    x = 250 - width / 2 - hmtx[names[0]][1] * scale
    d = []
    for n, a in zip(names, adv):
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        gs[n].draw(TransformPen(pen, (scale, 0, 0, -scale, x, base)))
        d.append(pen.getCommands())
        x += a + track
    return "".join(d)


def mark_svg(anim=False):
    out = []
    for i, (tone, d) in enumerate(PANELS):
        out.append(f'<path class="rdb-p rdb-{tone}" style="--i:{i}" d="{d}"/>')
    for i, (cx, cy, r, s, tone) in enumerate(LEAVES):
        out.append(
            f'<g transform="translate({cx} {cy}) rotate({r}) scale({s})">'
            f'<path class="rdb-leaf rdb-leaf-{tone}" fill-rule="evenodd" style="--i:{i}" d="{LEAF_PATH}"/></g>'
        )
    return "".join(out)


STATIC_CSS = (
    f".rdb-n{{fill:{NAVY}}}.rdb-b{{fill:{BLUE}}}.rdb-l{{fill:{LIGHT}}}"
    f".rdb-leaf-a{{fill:{LEAF}}}.rdb-leaf-s{{fill:{LEAF_SOFT}}}"
    f".rdb-w1{{fill:{NAVY}}}.rdb-w2{{fill:{BLUE}}}"
)
NEG_CSS = STATIC_CSS.replace(f".rdb-w1{{fill:{NAVY}}}.rdb-w2{{fill:{BLUE}}}", f".rdb-w1{{fill:#fff}}.rdb-w2{{fill:{LEAF}}}")
ANIM_CSS = """
.rdb-p{transform-box:fill-box;transform-origin:50% 50%;animation:rdbGlass .9s cubic-bezier(.2,.8,.2,1) both;animation-delay:calc(var(--i)*55ms)}
.rdb-leaf{transform-box:fill-box;transform-origin:50% 100%;animation:rdbLeafIn 1s cubic-bezier(.2,.8,.2,1) both,rdbSway 5.5s ease-in-out infinite;animation-delay:calc(.9s + var(--i)*90ms),calc(2s + var(--i)*-.6s)}
.rdb-word{animation:rdbRise 1s cubic-bezier(.2,.8,.2,1) both;animation-delay:1.1s}
.rdb-word.rdb-w2{animation-delay:1.35s}
@keyframes rdbGlass{from{opacity:0;transform:scale(.6) rotate(-6deg)}}
@keyframes rdbLeafIn{from{opacity:0;transform:translate(-40%,-60%) rotate(-90deg) scale(.3)}}
@keyframes rdbSway{0%,100%{rotate:0deg}50%{rotate:9deg}}
@keyframes rdbRise{from{opacity:0;transform:translateY(18px)}}
@media (prefers-reduced-motion:reduce){.rdb-p,.rdb-leaf,.rdb-word{animation:none}}
"""


def full_svg(words, css, bg=None, title="Reserva das Brisas"):
    rect = f'<rect x="-90" y="-60" width="680" height="820" fill="{bg}"/>' if bg else ""
    vb = "-90 -60 680 820" if bg else "-32 -2 564 706"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{title}">'
        f"<title>{title}</title><style>{css}</style>{rect}{mark_svg()}"
        f'<path class="rdb-word rdb-w1" d="{words["reserva"]}"/>'
        f'<path class="rdb-word rdb-w2" d="{words["brisas"]}"/></svg>\n'
    )


TOKEN = re.compile(r"\{\{(logo|basa):([a-z]+)(?::([a-z]+))?\}\}")


def basa_svg(tone, n):
    # Aproximação da marca Basa Inc; substituir pelo vetor oficial quando disponível
    neg = " neg" if tone == "neg" else ""
    gid = f"basaG{n}"
    return (
        f'<svg class="basa{neg}" viewBox="0 0 320 120" role="img" aria-label="Basa Inc">'
        f'<defs><linearGradient id="{gid}" x1="0" x2="1"><stop offset="0" stop-color="{NAVY}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient></defs>'
        '<text class="t1" x="0" y="66" font-family="Montserrat, sans-serif" font-weight="600" font-size="84" textLength="320" lengthAdjust="spacingAndGlyphs">BASA</text>'
        f'<rect x="0" y="80" width="228" height="16" fill="url(#{gid})"/>'
        '<text class="t2" x="236" y="104" font-family="Montserrat, sans-serif" font-weight="800" font-size="32" textLength="84" lengthAdjust="spacingAndGlyphs">INC</text></svg>'
    )


def inline_logo(kind, tone, words):
    cls = f"rdb {tone}" if tone else "rdb"
    w = f'<path class="rdb-word rdb-w1" d="{words["reserva"]}"/><path class="rdb-word rdb-w2" d="{words["brisas"]}"/>'
    if kind == "mark":
        return f'<svg class="{cls}" viewBox="0 0 500 500" aria-hidden="true">{mark_svg()}</svg>'
    if kind == "lockup":
        return f'<svg class="{cls}" viewBox="0 0 1560 500" role="img" aria-label="Reserva das Brisas">{mark_svg()}<g transform="translate(643 -754) scale(1.6)">{w}</g></svg>'
    return f'<svg class="{cls}" viewBox="-32 -2 564 706" role="img" aria-label="Reserva das Brisas">{mark_svg()}{w}</svg>'


def main(font_path=None):
    # O lettering só é recalculado quando a fonte é informada; senão usa o cache versionado
    cache = ROOT / "tools" / "wordmark.json"
    if font_path:
        words = {k: word_path(font_path, **v) for k, v in WORDS.items()}
        cache.write_text(json.dumps(words), encoding="utf-8")
    else:
        words = json.loads(cache.read_text(encoding="utf-8"))

    logo = ROOT / "logo"
    logo.mkdir(exist_ok=True)
    (logo / "reserva-das-brisas.svg").write_text(full_svg(words, STATIC_CSS, bg=SKY), encoding="utf-8")
    (logo / "reserva-das-brisas-transparente.svg").write_text(full_svg(words, STATIC_CSS), encoding="utf-8")
    (logo / "reserva-das-brisas-negativa.svg").write_text(full_svg(words, NEG_CSS), encoding="utf-8")
    (logo / "reserva-das-brisas-animada.svg").write_text(full_svg(words, STATIC_CSS + ANIM_CSS, bg=SKY), encoding="utf-8")
    (logo / "simbolo.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500"><style>{STATIC_CSS}</style>{mark_svg()}</svg>\n',
        encoding="utf-8",
    )

    counter = iter(range(100))
    def sub(m):
        kind, a, b = m.groups()
        if kind == "basa":
            return basa_svg(a, next(counter))
        return inline_logo(a, b, words)

    src = (ROOT / "src" / "index.src.html").read_text(encoding="utf-8")
    page = TOKEN.sub(sub, src)
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print("ok", len(page) // 1024, "KB")


if __name__ == "__main__":
    main(*sys.argv[1:2])
