#!/usr/bin/env python3
"""Build the site's original 1200 x 630 sharing artwork from vector primitives.

Offline authoring tool, never run by the site or publication workflow.
Requires fonttools[woff], Pillow and Inkscape. The sans/mono fonts are the site's
bundled fonts; serif lettering uses Debian's fonts-liberation package. All text
is outlined before rendering, so the resulting SVGs have no font dependency.
Run from any directory: python scripts/generate_social_cards.py
"""
from __future__ import annotations

import math
from pathlib import Path
import subprocess
import tempfile
from xml.sax.saxutils import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
TAU = math.tau
INK, IVORY, SAGE, MUTED, COPPER, BLUE = "#0c1715", "#f1efdf", "#cedcad", "#a8bcae", "#d29972", "#a5ccdd"


def font(path, weight=None):
    result = TTFont(path)
    if weight is not None:
        result = instantiateVariableFont(result, {"wght": weight}, inplace=False)
    return result


FONTS = {
    "serif": font("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"),
    "italic": font("/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"),
    "sans": font(OUT / "fonts/manrope-latin-wght-normal.woff2", 550),
    "mono": font(OUT / "fonts/jetbrains-mono-latin-wght-normal.woff2", 450),
}


def text(value, x, y, size, fill=IVORY, face="sans", tracking=0):
    """Outline text using exactly the same glyph positions in every renderer."""
    selected = FONTS[face]
    glyphs, cmap = selected.getGlyphSet(), selected.getBestCmap()
    scale = size / selected["head"].unitsPerEm
    paths, offset = [], 0.0
    for char in value:
        name = cmap.get(ord(char), ".notdef")
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        if pen.getCommands():
            paths.append(f'<path transform="translate({offset:.2f},0)" d="{pen.getCommands()}"/>')
        offset += selected["hmtx"].metrics[name][0] + tracking / scale
    return f'<g aria-label="{escape(value)}" fill="{fill}" transform="translate({x},{y}) scale({scale:.7f},{-scale:.7f})">{"".join(paths)}</g>'


def path(d, stroke=SAGE, width=1, opacity=1, fill="none", extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" opacity="{opacity}" {extra}/>'


def line(x1, y1, x2, y2, color="#3c5146", opacity=1):
    return path(f"M{x1} {y1} L{x2} {y2}", color, 1, opacity)


def rect(x, y, w, h, fill="none", stroke="#4c6255", r=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'


def circle(x, y, r, fill=SAGE, stroke="none"):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}"/>'


def form(cx=915, cy=306, scale=158, mode="weave"):
    """A still from the same parametric family as the interactive homepage."""
    shapes = []
    palette = [IVORY, SAGE, BLUE, COPPER, IVORY]
    for i in range(54):
        v = TAU * (i + .5) / 54
        points, depth = [], 0
        for j in range(193):
            u = TAU * j / 192
            if mode == "bloom":
                radius = .91 + .3 * math.cos(5 * u) + .18 * math.cos(v)
                x, y = radius * math.cos(u), radius * math.sin(u)
                z = .29 * math.sin(v) + .23 * math.sin(5*u) + .12 * math.cos(2*u)
            elif mode == "orbit":
                twist = v + .5 * math.sin(2 * u)
                radius = 1.02 + .3 * math.cos(twist)
                x, y = 1.08 * radius * math.cos(u), .94 * radius * math.sin(u)
                z = .31 * math.sin(twist) + .18 * math.sin(2 * u)
            else:
                tube = .19 + .035 * math.cos(3 * u)
                radius = .94 + .33 * math.cos(3 * u) + tube * math.cos(v)
                x, y = 1.07 * radius * math.cos(2 * u), radius * math.sin(2 * u)
                z = .42 * math.sin(3 * u) + tube * math.sin(v)
            # A fixed three-quarter camera, never an animation frame capture.
            yy = y * math.cos(.43) - z * math.sin(.43)
            zz = y * math.sin(.43) + z * math.cos(.43)
            xx = x * math.cos(-.35) + zz * math.sin(-.35)
            zz = -x * math.sin(-.35) + zz * math.cos(-.35)
            rx, ry = xx * math.cos(-.3) - yy * math.sin(-.3), xx * math.sin(-.3) + yy * math.cos(-.3)
            perspective = 4.8 / (4.8 - zz)
            points.append(f"{cx + rx * scale * perspective:.2f},{cy + ry * scale * perspective:.2f}")
            depth += zz
        shapes.append((depth, path("M" + " L".join(points), palette[min(4, i // 11)], .85, .75)))
    return "".join(item[1] for item in sorted(shapes))


def scaffold(kind, footer):
    return [
        '<defs><radialGradient id="glow"><stop stop-color="#27443a"/><stop offset="1" stop-color="#0c1715"/></radialGradient></defs>',
        f'<rect width="1200" height="630" fill="{INK}"/>',
        '<ellipse cx="942" cy="299" rx="570" ry="420" fill="url(#glow)"/>',
        text("suadtl", 58, 78, 42, face="serif"), circle(168, 74, 3, SAGE),
        text(kind.upper(), 62, 150, 12, MUTED, "mono", 1.6),
        line(60, 541, 1140, 541),
        text(footer, 62, 584, 13, MUTED, "mono"),
        text("arbiterforge.com", 951, 584, 13, SAGE, "mono"),
        path("M1121 63 L1137 63 L1137 79 M1137 63 L1117 83", MUTED, 1.4),
    ]


def title(lines, size=75, top=244, leading=77, italic_last=True):
    return "".join(text(s, 58, top + i * leading, size,
        SAGE if italic_last and i == len(lines)-1 else IVORY,
        "italic" if italic_last and i == len(lines)-1 else "serif") for i, s in enumerate(lines))


def flow():
    bits = []
    labels = [("01", "Route", 690, 230), ("02", "Evidence", 934, 230),
              ("03", "Review", 690, 377), ("04", "Decision", 934, 377)]
    bits += [path("M781 284 L1025 284 L1025 349 L781 349 L781 431 L934 431", "#8fa87e", 1.5)]
    for number, label, x, y in labels:
        active = number == "03"
        bits += [rect(x, y, 180, 105, "#21372c" if active else "#14251e", SAGE if active else "#4a6252"),
                 text(number, x+18, y+29, 11, MUTED, "mono"), text(label, x+18, y+72, 24, IVORY)]
    bits += [text("WORKFLOW STUDY", 693, 196, 11, MUTED, "mono", 1),
             text("The human decision stays explicit.", 693, 514, 12, MUTED)]
    return "".join(bits)


def network():
    bits = [rect(690, 203, 190, 277, "#10231f", "#48665b"),
            rect(906, 203, 222, 277, "#10231f", "#48665b"),
            text("NETWORK A", 711, 236, 11, MUTED, "mono"),
            text("SHARED SERVICES", 925, 236, 11, MUTED, "mono"),
            path("M785 337 L884 337 L884 299 L951 299 M884 337 L884 405 L951 405", BLUE, 2),
            path("M943 294 L951 299 L943 304 M943 400 L951 405 L943 410", BLUE, 1.5),
            rect(716, 309, 138, 58, "#294438", SAGE, 7), text("App portal", 732, 344, 18),
            rect(952, 270, 154, 58, "#233831", "#8fae9b", 7), text("Identity", 973, 305, 18),
            rect(952, 376, 154, 58, "#233831", "#8fae9b", 7), text("Monitoring", 966, 411, 18),
            text("FICTIONAL NETWORK STUDY", 693, 514, 11, MUTED, "mono", .5)]
    return "".join(bits)


def landscape():
    bits = [circle(1033, 217, 46, "#354d42"), circle(1033, 217, 32, "#13271f"),
            path("M680 460 L680 392 L735 366 L790 388 L847 350 L893 394 L938 409 L1000 363 L1059 350 L1140 397 L1140 460 Z", "#577965", 1.4, 1, "#1d332b"),
            path("M680 460 L680 425 L752 414 L809 436 L856 416 L930 443 L1025 405 L1099 423 L1140 409 L1140 460 Z", "#9db789", 1.3, 1, "#263f31"),
            path("M764 378 Q900 130 1069 367", COPPER, 1.8, 1, extra='stroke-dasharray="3 8"'),
            rect(744, 372, 32, 11, SAGE, SAGE, 4), line(760, 372, 774, 357, SAGE),
            rect(1050, 359, 32, 11, COPPER, COPPER, 4), line(1066, 359, 1052, 344, COPPER),
            text("WIND / AIM / TERRAIN", 691, 514, 11, MUTED, "mono", 1)]
    return "".join(bits)


def editorial():
    bits = [rect(726, 187, 387, 309, "#182920", "#4a6150"), text("ARBITER NEWS", 755, 225, 15, SAGE, "mono", 1),
            line(755, 247, 1083, 247)]
    for i, label in enumerate(["AI & developer tools", "Cloud & infrastructure", "Security & defense tech", "Markets & money"]):
        y = 285 + i * 57
        bits += [text(f"0{i+1}", 755, y, 11, MUTED, "mono"), text(label, 795, y, 17, IVORY), line(795, y+18, 1083, y+18)]
    return "".join(bits)


def notebook():
    bits = [rect(742, 182, 340, 314, "#202c21", "#58634a"), text("FROM THE NOTEBOOK", 770, 220, 11, MUTED, "mono", 1)]
    for x in [794, 903, 1012]:
        bits += [line(x, 280, x, 388, SAGE), line(x+12, 280, x+12, 388, SAGE), line(x-6, 280, x+18, 280, COPPER)]
    bits += [path("M765 334 L1055 334", SAGE, 1.3, extra='stroke-dasharray="5 7"'),
             circle(851, 334, 4, COPPER), circle(964, 334, 4, SAGE),
             text("Evidence. Review. Human judgment.", 769, 453, 14, MUTED)]
    return "".join(bits)


def project_studies():
    return (form(965, 255, 108, "orbit") +
            rect(702, 368, 421, 109, "#15271f", "#45604e") +
            text("01  codeArbiter", 725, 397, 16) +
            text("02  Service Integration Map", 725, 428, 16) +
            text("03  singedTerra", 725, 459, 16))


CARDS = {
    "home": ("Personal projects / suadtl", "Systems, tools, and experiments.",
        title(["Building systems,", "tools, and", "experiments."], 75) + form(910, 300, 146)),
    "projects": ("The workbench", "Selected builds / ongoing experiments",
        title(["Useful things.", "Interesting", "problems."], 76) + project_studies()),
    "lab": ("The generative studio", "Living geometry / made to be played with",
        title(["A little structure.", "A little play."], 74, 278, 88) +
        text("Shape it. Remix it. Make it yours.", 62, 441, 21, MUTED) + form(925, 308, 164, "bloom")),
    "news": ("Arbiter News / the reading habit", "Daily reading / original sources / an open archive",
        title(["The daily", "read."], 91, 278, 96) + text("AI-assisted. Source-linked.", 62, 445, 21, MUTED) + editorial()),
    "codearbiter": ("Project 01 / developer tooling", "codeArbiter / a project by suadtl",
        title(["codeArbiter"], 84, 260, italic_last=False) +
        text("Let agents build.", 62, 341, 43, IVORY, "serif") + text("Keep the evidence.", 62, 397, 43, SAGE, "italic") + flow()),
    "sim": ("Project 02 / infrastructure", "Service Integration Map / a project by suadtl",
        title(["See the services.", "Follow the", "dependencies."], 70) + network()),
    "singedterra": ("Project 03 / browser game", "singedTerra / a project by suadtl",
        title(["singedTerra"], 85, 264, italic_last=False) +
        text("A little aim.", 62, 350, 51, IVORY, "serif") + text("A lot of impact.", 62, 412, 51, SAGE, "italic") + landscape()),
    "essay": ("From the notebook / essay", "An early note on the thinking behind codeArbiter",
        title(["Why hard", "gates."], 96, 280, 101) + text("A note by suadtl.", 62, 452, 21, MUTED) + notebook()),
}


def main():
    source = OUT / "social"
    source.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="suadtl-social-") as scratch:
        for name, (kind, footer, drawing) in CARDS.items():
            svg = source / f"{name}.svg"
            svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img">'
                           f'<title>{escape(kind)}</title><desc>{escape(footer)}</desc>'
                           + "".join(scaffold(kind, footer)) + drawing + '</svg>\n')
            png = OUT / f"social-{name}.png"
            temporary_png = Path(scratch) / f"{name}.png"
            subprocess.run(["inkscape", str(svg), "--export-type=png", "--export-width=1200",
                            f"--export-filename={temporary_png}"], check=True, capture_output=True)
            # Lossless PNG optimization; no palette reduction or screenshot edits.
            with Image.open(temporary_png) as picture:
                picture.convert("RGB").save(png, optimize=True)
            print(f"{png.relative_to(ROOT)}: {png.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
