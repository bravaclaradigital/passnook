"""
PassNook — Asset Generator
Uses Segoe MDL2 Assets (Windows system icon font) for a crisp, native-quality lock glyph.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ASSETS = Path(__file__).parent / "assets"

BG1 = (91,  33, 182)   # #5B21B6
BG2 = (124, 58, 237)   # #7C3AED

# Segoe MDL2 Assets — E72E is the closed padlock used throughout Windows UI
MDL2_FONT  = "C:/Windows/Fonts/segmdl2.ttf"
LOCK_GLYPH = "\uE72E"


def _gradient(w, h):
    img = Image.new("RGB", (w, h))
    for y in range(h):
        t  = y / max(h - 1, 1)
        px = tuple(int(BG1[i] + (BG2[i] - BG1[i]) * t) for i in range(3))
        for x in range(w):
            img.putpixel((x, y), px)
    return img


def make_logo(size: int = 256) -> Image.Image:
    S      = size * 4          # 4× supersample, Lanczos back down
    pad    = int(S * 0.055)
    inner  = S - 2 * pad
    radius = int(S * 0.26)

    # ── Gradient rounded-square background ───────────────────────────────────
    bg = _gradient(inner, inner).convert("RGBA")
    mask = Image.new("L", (inner, inner), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, inner - 1, inner - 1], radius=radius, fill=255
    )
    bg.putalpha(mask)

    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    canvas.paste(bg, (pad, pad), bg)

    # ── Lock glyph from Segoe MDL2 Assets ────────────────────────────────────
    font_size = int(S * 0.56)
    try:
        font = ImageFont.truetype(MDL2_FONT, font_size)
    except OSError:
        # Fallback: Segoe UI Symbol also carries the glyph on some machines
        font = ImageFont.truetype("C:/Windows/Fonts/seguisym.ttf", font_size)

    d    = ImageDraw.Draw(canvas)
    bbox = d.textbbox((0, 0), LOCK_GLYPH, font=font)
    tw   = bbox[2] - bbox[0]
    th   = bbox[3] - bbox[1]
    tx   = (S - tw) // 2 - bbox[0]
    ty   = (S - th) // 2 - bbox[1] + int(S * 0.02)   # tiny optical nudge down

    d.text((tx, ty), LOCK_GLYPH, font=font, fill=(255, 255, 255, 245))

    return canvas.resize((size, size), Image.LANCZOS)


def _write_ico(path):
    sizes = [32, 48, 64, 128, 256]
    icons = [make_logo(s).convert("RGBA") for s in sizes]
    icons[0].save(
        str(path), format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=icons[1:],
        bitmap_format="png",
    )


def ensure_assets():
    ASSETS.mkdir(exist_ok=True)
    if not (ASSETS / "logo.png").exists():
        make_logo(256).save(str(ASSETS / "logo.png"))
    if not (ASSETS / "icon.ico").exists():
        _write_ico(ASSETS / "icon.ico")


if __name__ == "__main__":
    print("PassNook — generating assets...")
    ASSETS.mkdir(exist_ok=True)
    make_logo(256).save(str(ASSETS / "logo.png"))
    print("  OK logo.png")
    _write_ico(ASSETS / "icon.ico")
    print("  OK icon.ico")
    print("Done.")
