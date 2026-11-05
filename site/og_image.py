"""Open Graph images for Gearlist pages, 1200 x 630 PNG, in the style of social-preview.png.

Used by build_site.py. Needs Pillow and the Space Grotesk and Space Mono fonts. When
either is missing, `renderer()` returns None and the build uses the site-wide image.

Fonts are looked up in GEARLIST_FONT_DIR, then the usual font folders on macOS and Linux.
Space Grotesk may be the variable font (SpaceGrotesk[wght].ttf) or the static files.
"""
import math
import os
import re
from pathlib import Path

W, H = 1200, 630
INK = (20, 22, 26)
PANEL = (28, 31, 37)
GRID = (32, 34, 38)
CREAM = (244, 241, 232)
BODY = (185, 180, 166)
COLOURS = {
    "gold": (201, 161, 90),
    "pink": (232, 67, 143),
    "teal": (91, 192, 190),
    "cream": CREAM,
}

LEFT = 72
TILE_X, TILE_Y, TILE_W, TILE_H = 868, 118, 260, 300
TEXT_W = TILE_X - LEFT - 56
FOOT_Y = 556


def _font_dirs():
    env = os.environ.get("GEARLIST_FONT_DIR")
    home = Path.home()
    dirs = [Path(env)] if env else []
    dirs += [
        home / "Library/Fonts", Path("/Library/Fonts"), Path("/System/Library/Fonts"),
        home / ".local/share/fonts", home / ".fonts", Path("/usr/share/fonts"), Path("/usr/local/share/fonts"),
    ]
    return [d for d in dirs if d.is_dir()]


def _find(patterns):
    for folder in _font_dirs():
        for pattern in patterns:
            hits = sorted(folder.rglob(pattern))
            if hits:
                return hits[0]
    return None


def _load_fonts():
    from PIL import ImageFont

    variable = _find(["SpaceGrotesk[[]wght[]].ttf", "SpaceGrotesk-VariableFont*.ttf"])
    grotesk_bold = grotesk_regular = None
    if variable:
        grotesk_bold = grotesk_regular = variable
    else:
        grotesk_bold = _find(["SpaceGrotesk-Bold.ttf"])
        grotesk_regular = _find(["SpaceGrotesk-Regular.ttf"])
    mono_regular = _find(["SpaceMono-Regular.ttf"])
    mono_bold = _find(["SpaceMono-Bold.ttf"])
    if not all((grotesk_bold, grotesk_regular, mono_regular, mono_bold)):
        return None

    def grotesk(size, weight):
        path = grotesk_bold if weight >= 600 else grotesk_regular
        font = ImageFont.truetype(str(path), size)
        if path == variable:
            font.set_variation_by_axes([weight])
        return font

    def mono(size, bold=False):
        return ImageFont.truetype(str(mono_bold if bold else mono_regular), size)

    return grotesk, mono


# A small SVG path reader for the site's icons: M L H V C S Q A Z, absolute and relative.
_TOKEN = re.compile(r"[MmLlHhVvCcSsQqAaZz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _arc_points(x1, y1, rx, ry, phi, large, sweep, x2, y2, steps=24):
    """Endpoint to centre conversion from the SVG specification, appendix F.6.5."""
    if rx == 0 or ry == 0:
        return [(x2, y2)]
    rx, ry = abs(rx), abs(ry)
    cp, sp = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = cp * dx + sp * dy, -sp * dx + cp * dy
    lam = (x1p ** 2) / rx ** 2 + (y1p ** 2) / ry ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
    den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
    coef = math.sqrt(max(0.0, num / den)) if den else 0.0
    if large == sweep:
        coef = -coef
    cxp, cyp = coef * rx * y1p / ry, -coef * ry * x1p / rx
    cx = cp * cxp - sp * cyp + (x1 + x2) / 2
    cy = sp * cxp + cp * cyp + (y1 + y2) / 2

    def angle(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a

    t1 = angle(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = angle((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dt > 0:
        dt -= 2 * math.pi
    elif sweep and dt < 0:
        dt += 2 * math.pi
    out = []
    for i in range(1, steps + 1):
        t = t1 + dt * i / steps
        out.append((cx + rx * math.cos(t) * cp - ry * math.sin(t) * sp,
                    cy + rx * math.cos(t) * sp + ry * math.sin(t) * cp))
    return out


def _bezier(p0, p1, p2, p3, steps=16):
    out = []
    for i in range(1, steps + 1):
        t = i / steps
        u = 1 - t
        out.append((
            u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1],
        ))
    return out


def path_to_polylines(d):
    """Flattens an SVG path into a list of (points, closed) polylines."""
    tokens = _TOKEN.findall(d)
    i = 0
    cmd = None
    x = y = sx = sy = 0.0
    last_ctrl = None
    lines = []
    current = []

    def nums(n):
        nonlocal i
        vals = [float(t) for t in tokens[i:i + n]]
        i += n
        return vals

    def finish(closed=False):
        nonlocal current
        if len(current) > 1 or (current and closed):
            lines.append((current, closed))
        current = []

    while i < len(tokens):
        tok = tokens[i]
        if tok.isalpha():
            cmd = tok
            i += 1
            if cmd in "Zz":
                current.append((sx, sy))
                finish(closed=True)
                x, y = sx, sy
                current = [(x, y)]
                last_ctrl = None
                continue
        rel = cmd.islower()
        c = cmd.upper()
        if c == "M":
            finish()
            px, py = nums(2)
            x, y = (x + px, y + py) if rel else (px, py)
            sx, sy = x, y
            current = [(x, y)]
            cmd = "l" if rel else "L"
            last_ctrl = None
        elif c == "L":
            px, py = nums(2)
            x, y = (x + px, y + py) if rel else (px, py)
            current.append((x, y))
            last_ctrl = None
        elif c == "H":
            (px,) = nums(1)
            x = x + px if rel else px
            current.append((x, y))
            last_ctrl = None
        elif c == "V":
            (py,) = nums(1)
            y = y + py if rel else py
            current.append((x, y))
            last_ctrl = None
        elif c in "CS":
            if c == "C":
                x1, y1, x2, y2, px, py = nums(6)
                if rel:
                    x1, y1, x2, y2 = x + x1, y + y1, x + x2, y + y2
            else:
                x2, y2, px, py = nums(4)
                if rel:
                    x2, y2 = x + x2, y + y2
                x1, y1 = (2 * x - last_ctrl[0], 2 * y - last_ctrl[1]) if last_ctrl else (x, y)
            if rel:
                px, py = x + px, y + py
            current += _bezier((x, y), (x1, y1), (x2, y2), (px, py))
            last_ctrl = (x2, y2)
            x, y = px, py
        elif c == "Q":
            x1, y1, px, py = nums(4)
            if rel:
                x1, y1, px, py = x + x1, y + y1, x + px, y + py
            c1 = (x + 2 / 3 * (x1 - x), y + 2 / 3 * (y1 - y))
            c2 = (px + 2 / 3 * (x1 - px), py + 2 / 3 * (y1 - py))
            current += _bezier((x, y), c1, c2, (px, py))
            last_ctrl = None
            x, y = px, py
        elif c == "A":
            rx, ry, phi, large, sweep, px, py = nums(7)
            if rel:
                px, py = x + px, y + py
            current += _arc_points(x, y, rx, ry, phi, int(large), int(sweep), px, py)
            last_ctrl = None
            x, y = px, py
        else:
            raise ValueError(f"unsupported path command {cmd}")
    finish()
    return lines


def _draw_icon(img, path_d, colour, box, size):
    """Draws a 24 x 24 stroked icon, supersampled four times for smooth edges."""
    from PIL import Image, ImageDraw

    ss = 4
    big = size * ss
    scale = big / 24
    width = max(1, round(2.25 * scale))
    layer = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    r = width / 2
    for points, closed in path_to_polylines(path_d):
        pts = [(px * scale, py * scale) for px, py in points]
        draw.line(pts, fill=colour + (255,), width=width, joint="curve")
        ends = pts if closed else [pts[0], pts[-1]]
        for ex, ey in ends:
            draw.ellipse((ex - r, ey - r, ex + r, ey + r), fill=colour + (255,))
    small = layer.resize((size, size), Image.LANCZOS)
    img.alpha_composite(small, box)


def _wrap(draw, text, font, width, max_lines):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            line = trial
            continue
        if line:
            lines.append(line)
        line = word
        if len(lines) == max_lines:
            break
    else:
        if line:
            lines.append(line)
        return lines, False
    # Too long: trim the last line and end it with an ellipsis.
    lines = lines[:max_lines]
    last = lines[-1]
    while last and draw.textlength(last + "…", font=font) > width:
        last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
    lines[-1] = last.rstrip(",;:.") + "…"
    return lines, True


def _tracked(draw, xy, text, font, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def renderer():
    """Returns render(path, **card) or None when Pillow or the fonts are missing."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    fonts = _load_fonts()
    if not fonts:
        return None
    grotesk, mono = fonts
    eyebrow_font = mono(22)
    slug_font = mono(24)
    foot_font = mono(22)
    tile_label = mono(28, bold=True)
    tile_sub = mono(19)
    desc_font = grotesk(30, 400)
    name_fonts = {size: grotesk(size, 700) for size in range(96, 47, -4)}

    def render(path, *, eyebrow, title, subtitle, text, colour, icon_path, tile_title, tile_text, footer):
        accent = COLOURS.get(colour, COLOURS["gold"])
        img = Image.new("RGBA", (W, H), INK + (255,))
        draw = ImageDraw.Draw(img)
        for gx in range(59, W, 60):
            draw.line([(gx, 0), (gx, H)], fill=GRID, width=1)
        for gy in range(59, H, 60):
            draw.line([(0, gy), (W, gy)], fill=GRID, width=1)
        draw.rectangle((0, 0, W, 11), fill=COLOURS["gold"])

        # Left column: eyebrow, title, optional subtitle, description.
        y = 84
        _tracked(draw, (LEFT, y), eyebrow.upper(), eyebrow_font, COLOURS["gold"], 6)
        y += 52
        for size, font in name_fonts.items():
            lines, cut = _wrap(draw, title, font, TEXT_W, 2)
            if not cut:
                break
        line_h = round(size * 1.04)
        for line in lines:
            draw.text((LEFT - 3, y), line, font=font, fill=CREAM)
            y += line_h
        y += 14
        if subtitle:
            draw.text((LEFT, y), subtitle, font=slug_font, fill=BODY)
            y += 44
        y += 10
        desc_h = 40
        room = max(1, min(3, (FOOT_Y - 30 - y) // desc_h))
        for line in _wrap(draw, text, desc_font, TEXT_W, room)[0]:
            draw.text((LEFT, y), line, font=desc_font, fill=BODY)
            y += desc_h

        # Right: one kit tile with the group icon, as on the social card.
        shadow = 12
        draw.rectangle((TILE_X + shadow, TILE_Y + shadow, TILE_X + TILE_W + shadow, TILE_Y + TILE_H + shadow), fill=accent)
        draw.rectangle((TILE_X, TILE_Y, TILE_X + TILE_W, TILE_Y + TILE_H), fill=PANEL, outline=CREAM, width=4)
        _draw_icon(img, icon_path, accent, (TILE_X + 28, TILE_Y + 30), 96)
        draw.text((TILE_X + 28, TILE_Y + TILE_H - 92), tile_title, font=tile_label, fill=CREAM)
        draw.text((TILE_X + 28, TILE_Y + TILE_H - 46), tile_text, font=tile_sub, fill=BODY)

        # Footer: the page address and the publisher.
        right = "by Tech Horizon Labs"
        right_w = draw.textlength(right, font=foot_font)
        draw.text((LEFT, FOOT_Y), footer, font=foot_font, fill=BODY)
        if LEFT + draw.textlength(footer, font=foot_font) + 40 < W - LEFT - right_w:
            draw.text((W - LEFT - right_w, FOOT_Y), right, font=foot_font, fill=BODY)

        out = img.convert("RGB").quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        path.parent.mkdir(parents=True, exist_ok=True)
        out.save(path, format="PNG", optimize=True)

    return render
