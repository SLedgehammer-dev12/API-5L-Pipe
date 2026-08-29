#!/usr/bin/env python3
"""
Generate the application icon for API 5L Pipe QA/QC & Wall Thickness Design Suite.

Design: dark slate rounded square + a 3D-looking pipe (cylinder with wall thickness
and an amber weld seam) + a bold 3D-extruded "API" wordmark. No BOTAŞ, no "5L".

Outputs:
  static/icon/icon_preview.png   (1024 px preview for approval)
  static/icon/app_icon.ico       (Windows: 16..256 px)
  static/icon/app_icon.icns      (macOS: 16..1024 px)

Requires Pillow (dev-time only; not a runtime dependency).
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SIZE = 1024
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static", "icon")
OUT_DIR = os.path.abspath(OUT_DIR)

# Palette (matches the app theme)
BG_TOP = (10, 18, 32)        # slate-950
BG_BOTTOM = (30, 41, 59)     # slate-800
PIPE_LIGHT = (59, 130, 246)  # blue-500
PIPE_MID = (37, 99, 235)     # blue-600
PIPE_DARK = (29, 78, 216)    # blue-700
PIPE_INNER = (15, 23, 42)    # slate-900 (inner bore)
WELD = (245, 158, 11)        # amber-500
SHADOW = (2, 6, 16)


def find_bold_font(size: int):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default(size=size)


def vgrad(w, h, top, bottom):
    base = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(base)
    for y in range(h):
        t = y / max(1, h - 1)
        col = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=col)
    return base


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg = vgrad(size, size, BG_TOP, BG_BOTTOM)
    bg = bg.convert("RGBA")

    # rounded-square mask
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 0.19), fill=255)
    img = Image.composite(bg, img, mask)

    d = ImageDraw.Draw(img)

    s = size / 1024.0  # scale factor

    # ---------- 3D pipe (horizontal cylinder, open ends, weld seam) ----------
    pipe_top = int(150 * s)
    pipe_bottom = int(430 * s)
    pipe_left = int(150 * s)
    pipe_right = int(874 * s)
    rx = int(56 * s)          # end-cap half-width
    ry = (pipe_bottom - pipe_top) // 2

    # cylinder body with vertical shading
    body = vgrad(pipe_right - pipe_left, pipe_bottom - pipe_top, PIPE_LIGHT, PIPE_DARK)
    img.paste(body, (pipe_left, pipe_top), mask=None)

    # end-cap ellipse (right, open end) -> darker bore ring
    d.ellipse([pipe_right - rx, pipe_top, pipe_right + rx, pipe_bottom], fill=PIPE_DARK)
    d.ellipse([pipe_right - int(rx * 0.45), pipe_top + int(ry * 0.18),
               pipe_right + int(rx * 0.45), pipe_bottom - int(ry * 0.18)],
              fill=PIPE_INNER)

    # left end cap (closed/back face hint)
    d.ellipse([pipe_left - rx, pipe_top, pipe_left + rx, pipe_bottom], fill=PIPE_MID)

    # top highlight
    hl = int(26 * s)
    d.rounded_rectangle([pipe_left, pipe_top, pipe_right, pipe_top + hl],
                        radius=hl // 2, fill=(96, 165, 250, 120))

    # amber weld seam along the top
    seam_y = pipe_top + int(52 * s)
    seam = vgrad(pipe_right - pipe_left, int(14 * s), WELD, (217, 119, 6))
    img.paste(seam, (pipe_left, seam_y), mask=None)
    d.line([(pipe_left + int(8 * s), seam_y + int(2 * s)),
            (pipe_right - int(8 * s), seam_y + int(2 * s))],
           fill=(255, 210, 120), width=int(4 * s))

    # soft drop shadow under pipe
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([pipe_left - int(60 * s), pipe_bottom + int(30 * s),
                pipe_right + int(60 * s), pipe_bottom + int(90 * s)], fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(int(30 * s)))
    img.alpha_composite(shadow)

    # ---------- "API" wordmark (3D extrusion) ----------
    font = find_bold_font(int(300 * s))
    text = "API"
    cx = size // 2
    ty = int(500 * s)
    anchor = "ma"

    def text_bbox_text(txt, fnt, ox=0, oy=0):
        b = d.textbbox((cx + ox, ty + oy), txt, font=fnt, anchor=anchor, stroke_width=0)
        return b

    # measure to center horizontally
    bb = d.textbbox((0, 0), text, font=font, anchor="ma", stroke_width=0)
    tw = bb[2] - bb[0]
    x0 = cx - tw // 2
    # extruded layers (depth)
    for off in (int(26 * s), int(18 * s), int(10 * s)):
        d.text((x0 + off, ty + off), text, font=font, fill=SHADOW, anchor="la")
    # soft glow behind text
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((x0, ty), text, font=font, fill=(59, 130, 246, 150), anchor="la")
    glow = glow.filter(ImageFilter.GaussianBlur(int(22 * s)))
    img.alpha_composite(glow)
    # main white text
    d.text((x0, ty), text, font=font, fill=(255, 255, 255), anchor="la")

    return img


def save_ico(img: Image.Image, path: str):
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = [img.resize(s, Image.LANCZOS).convert("RGBA") for s in sizes]
    images[0].save(path, format="ICO", sizes=sizes, append_images=images[1:])


def save_icns(img: Image.Image, path: str):
    sizes = [(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)]
    images = [img.resize(s, Image.LANCZOS).convert("RGBA") for s in sizes]
    try:
        images[0].save(path, format="ICNS", append_images=images[1:], scale=True)
    except Exception as e:  # noqa: BLE001
        print(f"  [uyarı] ICNS kaydedilemedi: {e}")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    icon = draw_icon(SIZE)

    preview = os.path.join(OUT_DIR, "icon_preview.png")
    icon.convert("RGB").save(preview)
    print("preview:", preview)

    ico = os.path.join(OUT_DIR, "app_icon.ico")
    save_ico(icon, ico)
    print("ico:", ico)

    icns = os.path.join(OUT_DIR, "app_icon.icns")
    save_icns(icon, icns)
    print("icns:", icns)

    for f in (preview, ico, icns):
        if os.path.exists(f):
            print("  ok:", os.path.getsize(f), "bytes")


if __name__ == "__main__":
    main()