#!/usr/bin/env python3
"""Compose the v5 front page for news-image-20261120.

A photo-magazine cover, full-bleed: the burning Kyiv bridge fills the top
~70% of the page, with a small white masthead, a red date ribbon, and the
headline set in white over a dark scrim at the foot of the photo. The bottom
~30% is a dark band with three small photo stories and a one-line in-brief.

All four photographs are AI-generated photorealistic images stored in
assets/ (see README.md). This script only crops, scales and lays them out
with PIL; it never draws the photos themselves.

Run:  python3 compose.py   ->  writes entry.png next to this file.
"""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"

PAGE_W = 1024
PAGE_H = 1024
HERO_H = 716            # hero photo occupies the top ~70%
BAND_Y = HERO_H         # dark bottom band starts here
MAX_BYTES = 1024 * 1024

HERO_SRC = ASSETS / "media-generation-hero-kyiv-bridge-0-24f23493-7429-4763-a588-32b0147f6386.jpg"
DRONE_SRC = ASSETS / "media-generation-ukraine-drones-0-1059ed6b-5e64-42af-9002-1b6c13e97b66.jpg"
STOCKS_SRC = ASSETS / "media-generation-taiwan-stocks-0-e4fff08d-f5f7-4b04-ba74-006424490fcb.jpg"
BASEBALL_SRC = ASSETS / "media-generation-baseball-stadium-0-18e4eccd-491b-4d86-a89b-42764e56f5ea.jpg"

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_BOLD = os.path.join(FONT_DIR, "liberation/LiberationSerif-Bold.ttf")
SERIF_ITALIC = os.path.join(FONT_DIR, "liberation/LiberationSerif-Italic.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "liberation/LiberationSans-Bold.ttf")
SANS_REG = os.path.join(FONT_DIR, "liberation/LiberationSans-Regular.ttf")

WHITE = (255, 255, 255)
OFFWHITE = (238, 238, 232)
RED = (178, 34, 24)          # date ribbon red
DARK = (16, 16, 18)           # bottom band
MUTED = (168, 168, 160)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def cover_crop(img: Image.Image, target_w: int, target_h: int,
               focus_y: float = 0.5) -> Image.Image:
    """Resize + centre-crop so the image exactly fills target_w x target_h.

    focus_y (0..1) picks the vertical centre of the crop window, so a
    subject sitting high or low in the frame can be kept in view.
    """
    scale = max(target_w / img.width, target_h / img.height)
    new_w = max(target_w, round(img.width * scale))
    new_h = max(target_h, round(img.height * scale))
    img = img.resize((new_w, new_h), Image.LANCZOS)
    x0 = (new_w - target_w) // 2
    span = new_h - target_h
    y0 = round(span * focus_y)
    return img.crop((x0, y0, x0 + target_w, y0 + target_h))


def fit_font(path: str, text: str, max_width: int,
             start_size: int, min_size: int = 12) -> ImageFont.FreeTypeFont:
    """Largest font size (down to min_size) at which text fits max_width."""
    size = start_size
    while size > min_size:
        f = font(path, size)
        if f.getlength(text) <= max_width:
            return f
        size -= 1
    return font(path, min_size)


def tracked_width(f: ImageFont.FreeTypeFont, text: str, tracking: int) -> int:
    return sum(f.getlength(ch) for ch in text) + tracking * max(len(text) - 1, 0)


def draw_tracked(draw: ImageDraw.ImageDraw, xy, text: str,
                 f: ImageFont.FreeTypeFont, fill, tracking: int = 2) -> None:
    """Draw text with letter-spacing; xy is the top-left of the first glyph."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += f.getlength(ch) + tracking


def draw_centered_tracked(draw: ImageDraw.ImageDraw, cx: int, y: int,
                          text: str, f: ImageFont.FreeTypeFont, fill,
                          tracking: int = 2) -> None:
    w = tracked_width(f, text, tracking)
    draw_tracked(draw, (cx - w // 2, y), text, f, fill, tracking)


def wrap_text(text: str, f: ImageFont.FreeTypeFont, max_width: int,
              max_lines: int = 2) -> list[str]:
    """Greedy word wrap into at most max_lines lines.

    Any leftover words are shown as an ellipsis on the final line, so
    text is never silently dropped.
    """
    words = text.split()
    lines: list[str] = []
    cur = ""
    idx = 0
    while idx < len(words):
        word = words[idx]
        trial = f"{cur} {word}".strip()
        if f.getlength(trial) <= max_width:
            cur = trial
            idx += 1
            continue
        if cur:
            lines.append(cur)
            cur = ""
            if len(lines) == max_lines:
                break
            continue
        # A single word alone is wider than the box: force it on a line.
        lines.append(word)
        idx += 1
        if len(lines) == max_lines:
            break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if idx < len(words) and lines:
        last = lines[-1]
        while last and f.getlength(last + " \u2026") > max_width:
            last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
        lines[-1] = f"{last} \u2026".strip()
    return lines[:max_lines]


def vertical_scrim(page: Image.Image, y_top: int, y_bottom: int,
                   max_alpha: int) -> None:
    """Fade a black gradient over [y_top, y_bottom] (transparent at top)."""
    height = y_bottom - y_top
    if height <= 0:
        return
    scrim = Image.new("RGBA", (PAGE_W, height), (0, 0, 0, 0))
    px = scrim.load()
    for y in range(height):
        a = round(max_alpha * (y / max(height - 1, 1)))
        for x in range(PAGE_W):
            px[x, y] = (0, 0, 0, a)
    page.alpha_composite(scrim, (0, y_top))


def main() -> int:
    for src in (HERO_SRC, DRONE_SRC, STOCKS_SRC, BASEBALL_SRC):
        if not src.is_file():
            print(f"error: missing {src}")
            return 1

    page = Image.new("RGB", (PAGE_W, PAGE_H), DARK)

    # ---- Hero photo, full-bleed top -------------------------------------
    hero = Image.open(HERO_SRC).convert("RGB")
    hero = cover_crop(hero, PAGE_W, HERO_H, focus_y=0.45)
    page.paste(hero, (0, 0))

    # Scrims so the white type stays readable over the photo.
    page_rgba = page.convert("RGBA")
    vertical_scrim(page_rgba, 0, 120, 110)        # top, under the masthead
    vertical_scrim(page_rgba, 430, HERO_H, 205)   # bottom, under the headline
    page = page_rgba.convert("RGB")
    draw = ImageDraw.Draw(page)

    # ---- Masthead ---------------------------------------------------------
    masthead = "THE WORLD TODAY"
    mast_font = font(SANS_BOLD, 34)
    draw_tracked(draw, (28, 30), masthead, mast_font, WHITE, tracking=4)
    mast_w = tracked_width(mast_font, masthead, 4)
    draw.rectangle([28, 78, 28 + mast_w, 82], fill=RED)

    # ---- Date ribbon ------------------------------------------------------
    ribbon_y, ribbon_h = 118, 50
    draw.rectangle([0, ribbon_y, PAGE_W, ribbon_y + ribbon_h], fill=RED)
    date_font = font(SANS_BOLD, 30)
    draw_centered_tracked(draw, PAGE_W // 2, ribbon_y + 9,
                          "FRIDAY, NOVEMBER 20, 2026", date_font, WHITE,
                          tracking=3)

    # ---- Headline + sub-headline over the dark foot of the photo ---------
    headline = "KYIV\u2019S BRIDGES BURN"
    head_font = fit_font(SERIF_BOLD, headline, PAGE_W - 56, 92)
    # Soft shadow so the white serif holds against smoke and flame.
    for dx, dy in ((2, 2), (-1, 1)):
        draw.text((28 + dx, 536 + dy), headline, font=head_font,
                  fill=(0, 0, 0))
    draw.text((28, 536), headline, font=head_font, fill=WHITE)

    sub = ("Russian ballistic missiles struck the North and South bridges "
           "overnight \u2014 power and water cut across the capital.")
    sub_font = font(SERIF_ITALIC, 27)
    sub_lines = wrap_text(sub, sub_font, PAGE_W - 56, max_lines=2)
    y = 640
    for line in sub_lines:
        draw.text((28, y), line, font=sub_font, fill=OFFWHITE)
        y += 34

    # ---- Bottom dark band: three photo stories ---------------------------
    draw = ImageDraw.Draw(page)
    margin = 24
    gap = 16
    photo_w = (PAGE_W - 2 * margin - 2 * gap) // 3   # 312
    photo_h = 184
    photo_y = BAND_Y + 18
    cap_y = photo_y + photo_h + 10

    stories = [
        (DRONE_SRC, "UK pledges 1,000+ drones for Kyiv", 0.45),
        (STOCKS_SRC, "Taiwan stocks plunge 2,200 points", 0.5),
        (BASEBALL_SRC, "Trump pardons Pete Rose", 0.5),
    ]
    for i, (src, caption, focus) in enumerate(stories):
        x = margin + i * (photo_w + gap)
        thumb = Image.open(src).convert("RGB")
        thumb = cover_crop(thumb, photo_w, photo_h, focus_y=focus)
        page.paste(thumb, (x, photo_y))
        draw.rectangle([x, photo_y, x + photo_w, photo_y + 3], fill=RED)
        cap_font = fit_font(SANS_BOLD, caption, photo_w, 21)
        draw.text((x, cap_y), caption, font=cap_font, fill=WHITE)

    # ---- In-brief line ----------------------------------------------------
    brief_y = cap_y + 34
    draw.line([margin, brief_y - 8, PAGE_W - margin, brief_y - 8],
              fill=(70, 70, 72), width=1)
    label = "IN BRIEF  "
    label_font = font(SANS_BOLD, 19)
    label_w = label_font.getlength(label)
    draw.text((margin, brief_y), label, font=label_font, fill=(214, 69, 55))
    brief = ("Houthi missile hits Riyadh\u2019s tallest tower  \u2022  "
             "US sanctions Comancheros & \u2019Ndrangheta  \u2022  "
             "13,000 protest in Tokyo")
    brief_font = fit_font(SANS_REG, brief, PAGE_W - 2 * margin - label_w,
                          19)
    draw.text((margin + label_w, brief_y), brief, font=brief_font,
              fill=OFFWHITE)

    # ---- Footer -----------------------------------------------------------
    footer = ("theworld.today  \u2014  All the news of Friday, November 20, "
              "2026, on one page.")
    foot_font = font(SANS_REG, 13)
    fw = foot_font.getlength(footer)
    draw.text(((PAGE_W - fw) / 2, PAGE_H - 22), footer, font=foot_font,
              fill=MUTED)

    out = HERE / "entry.png"
    page.save(out, "PNG", optimize=True)
    size = out.stat().st_size
    if size > MAX_BYTES:
        # Photographic PNG can overshoot 1 MiB; JPEG at high quality is
        # also accepted by the harness, so fall back to it (same filename).
        page.save(out, "JPEG", quality=92, optimize=True)
        size = out.stat().st_size
    print(f"wrote {out} ({size} bytes, {PAGE_W}x{PAGE_H})")
    if size > MAX_BYTES:
        print(f"error: still over {MAX_BYTES} bytes")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
