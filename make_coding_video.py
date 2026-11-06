"""Render a looping, illustrative coding scene for the studio section."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import math
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio_ffmpeg


ROOT = Path(__file__).parent
OUT = ROOT / "media"
W, H, FPS, DURATION = 1280, 560, 16, 8
FONT = "C:/Windows/Fonts/consola.ttf"
CODE = [
    [("import ", "muted"), ("{ createExperience }", "cyan"), (" from ", "muted"), ("'@neocode/core'", "yellow")],
    [],
    [("type ", "purple"), ("Project", "white"), (" = {", "muted")],
    [("  vision", "white"), (": ", "muted"), ("'inspire people'", "yellow"), (",", "muted")],
    [("  platform", "white"), (": [", "muted"), ("'web'", "yellow"), (", ", "muted"), ("'mobile'", "yellow"), ("],", "muted")],
    [("  experience", "white"), (": ", "muted"), ("'thoughtful'", "yellow")],
    [("}", "muted")],
    [],
    [("export async function ", "purple"), ("build", "cyan"), ("(project: Project) {", "white")],
    [("  const ", "purple"), ("idea", "white"), (" = ", "muted"), ("await ", "purple"), ("understand", "cyan"), ("(project)", "white")],
    [("  const ", "purple"), ("design", "white"), (" = ", "muted"), ("shape", "cyan"), ("(idea)", "white")],
    [("  const ", "purple"), ("product", "white"), (" = ", "muted"), ("await ", "purple"), ("createExperience", "cyan"), ("(design)", "white")],
    [("  return ", "purple"), ("product", "white")],
    [("}", "muted")],
]
COLORS = {
    "muted": (139, 160, 190),
    "white": (226, 232, 248),
    "cyan": (93, 213, 224),
    "purple": (145, 176, 255),
    "yellow": (251, 185, 139),
}


@lru_cache(maxsize=None)
def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size)


def background() -> Image.Image:
    image = Image.new("RGB", (W, H))
    pixels = image.load()
    for y in range(H):
        for x in range(W):
            glow = max(0, 1 - math.hypot((x - 1020) / 630, (y - 80) / 440))
            blue_glow = max(0, 1 - math.hypot((x - 700) / 450, (y + 55) / 370))
            pixels[x, y] = (
                int(5 + glow * 25 + blue_glow * 5),
                int(18 + glow * 26 + blue_glow * 12),
                int(32 + glow * 40 + blue_glow * 32),
            )

    blur = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(blur)
    d.ellipse((680, -120, 930, 160), fill=(58, 119, 238, 95))
    d.ellipse((1050, 210, 1390, 500), fill=(52, 103, 219, 75))
    d.ellipse((590, 330, 910, 640), fill=(51, 126, 237, 55))
    blur = blur.filter(ImageFilter.GaussianBlur(95))
    image = Image.alpha_composite(image.convert("RGBA"), blur)

    d = ImageDraw.Draw(image)
    d.rounded_rectangle((430, 8, 1035, 380), radius=10, fill=(27, 39, 61, 110), outline=(91, 105, 138, 65), width=2)
    for i in range(4):
        x = 475 + i * 116
        d.rounded_rectangle((x, 72, x + 83, 248), radius=8, outline=(90, 112, 157, 48), width=3)
        d.rectangle((x + 15, 92, x + 65, 99), fill=(100, 126, 164, 50))
    d.rounded_rectangle((647, 24, 1262, 480), radius=12, fill=(4, 11, 23, 255), outline=(49, 78, 111, 255), width=7)
    d.rounded_rectangle((660, 37, 1250, 467), radius=6, fill=(10, 21, 38, 255))
    d.rectangle((660, 37, 1250, 70), fill=(22, 37, 59, 255))
    d.ellipse((676, 49, 683, 56), fill=(92, 159, 255))
    d.ellipse((690, 49, 697, 56), fill=(255, 196, 105))
    d.ellipse((704, 49, 711, 56), fill=(99, 202, 175))
    d.text((733, 45), "experience.ts  •  NEOCODE", font=font(13), fill=(163, 184, 210))
    d.rectangle((664, 71, 710, 464), fill=(14, 29, 49))
    for i, color in enumerate([(92, 159, 255), (95, 178, 226), (137, 137, 218), (91, 201, 202)]):
        d.rounded_rectangle((679, 95 + i * 42, 694, 110 + i * 42), radius=3, outline=color, width=2)
    d.line((710, 70, 710, 466), fill=(42, 63, 88), width=2)
    d.rectangle((660, 440, 1250, 467), fill=(25, 48, 74))
    d.text((725, 446), "main  ✓  TypeScript", font=font(11), fill=(156, 196, 220))

    foreground = Image.new("RGBA", (W, H))
    f = ImageDraw.Draw(foreground)
    f.ellipse((865, 487, 1135, 670), fill=(23, 18, 36, 230))
    f.ellipse((1080, 486, 1335, 677), fill=(29, 21, 42, 230))
    f.polygon([(788, 560), (912, 494), (1058, 541), (992, 626)], fill=(30, 25, 45, 180))
    image = Image.alpha_composite(image, foreground.filter(ImageFilter.GaussianBlur(24)))
    return image.convert("RGB")


BASE = background()


def frame(t: float) -> Image.Image:
    image = BASE.copy()
    sweep = int(780 + 370 * ((t / DURATION) % 1))
    reflection = Image.new("RGBA", (W, H))
    ImageDraw.Draw(reflection).polygon(
        [(sweep, 72), (sweep + 62, 72), (sweep - 42, 439), (sweep - 104, 439)],
        fill=(112, 158, 211, 13),
    )
    image = Image.alpha_composite(image.convert("RGBA"), reflection).convert("RGB")
    d = ImageDraw.Draw(image)
    opacity = 0.88 + 0.12 * math.sin(t * math.pi / 4) ** 2
    for number, parts in enumerate(CODE, 1):
        y = 83 + (number - 1) * 24
        d.text((721, y), f"{number:02}", font=font(13), fill=(75, 100, 132))
        x = 761
        for value, token in parts:
            color = tuple(int(channel * opacity) for channel in COLORS[token])
            d.text((x, y - 1), value, font=font(15), fill=color)
            x += d.textlength(value, font=font(15))

    typing = "  await launch(product)"
    visible = int((t % 4) / 4 * (len(typing) + 6))
    text = typing[:min(len(typing), visible)]
    y = 83 + len(CODE) * 24
    d.text((721, y), "15", font=font(13), fill=(75, 100, 132))
    d.text((761, y - 1), text, font=font(15), fill=(110, 210, 219))
    if int(t * 2) % 2 == 0:
        x = 761 + d.textlength(text, font=font(15))
        d.rectangle((x, y, x + 2, y + 17), fill=(92, 159, 255))

    veil = Image.new("RGBA", (W, H))
    vd = ImageDraw.Draw(veil)
    vd.rectangle((0, 0, W, H), fill=(1, 11, 25, 17))
    vd.rectangle((0, 0, 660, H), fill=(1, 12, 24, 60))
    image = Image.alpha_composite(image.convert("RGBA"), veil)
    return image.convert("RGB")


def encode() -> None:
    OUT.mkdir(exist_ok=True)
    frame(6.5).save(OUT / "coding-studio-poster.jpg", quality=90)
    video = OUT / "coding-studio.mp4"
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for index in range(FPS * DURATION):
            process.stdin.write(frame(index / FPS).tobytes())
        process.stdin.close()
        error = process.stderr.read().decode(errors="replace")
        if process.wait() != 0:
            raise RuntimeError(error)
    finally:
        if process.poll() is None:
            process.kill()
    print(video)


if __name__ == "__main__":
    encode()
