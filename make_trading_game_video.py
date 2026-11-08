"""Render the trading-game chart film in Korean and English.

The supplied mockup is a visual reference. Every frame is drawn from shapes and
text, so the chart and copy can animate independently and remain crisp.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import math
import random
import subprocess

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg


ROOT = Path(__file__).parent
OUT = ROOT / "media"
OUT.mkdir(exist_ok=True)
W, H, FPS, DURATION = 1600, 690, 20, 9
NAVY = (4, 22, 38)
CORAL = (255, 78, 119)
ACCENT = (94, 157, 255)
WHITE = (247, 249, 255)
BLUE = (80, 133, 234)
FONT_REGULAR = "C:/Windows/Fonts/malgun.ttf"
FONT_BOLD = "C:/Windows/Fonts/malgunbd.ttf"


@lru_cache(maxsize=None)
def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def width(text: str, size: int, bold: bool = True) -> int:
    box = font(size, bold).getbbox(text)
    return box[2] - box[0]


def smooth(start: float, end: float, value: float) -> float:
    v = max(0.0, min(1.0, (value - start) / (end - start)))
    return v * v * (3 - 2 * v)


def fade_layer(base: Image.Image, layer: Image.Image, opacity: float, rise: int = 0) -> Image.Image:
    if opacity <= 0:
        return base
    opacity = min(1.0, opacity)
    overlay = layer.copy()
    overlay.putalpha(overlay.getchannel("A").point(lambda a: int(a * opacity)))
    base.alpha_composite(overlay, (0, int((1 - opacity) * rise)))
    return base


def add_line(draw: ImageDraw.ImageDraw, segments: list[tuple[str, tuple[int, int, int]]], y: int, size: int) -> None:
    total = sum(width(s, size) for s, _ in segments)
    x = (W - total) // 2
    for value, color in segments:
        draw.text((x + 2, y + 3), value, font=font(size, True), fill=(0, 0, 0, 170))
        draw.text((x, y), value, font=font(size, True), fill=(*color, 255))
        x += width(value, size)


COPY = {
    "ko": {
        "intro": "기본적 분석? 기술적 분석? 많이 헷갈리고 어렵습니다.",
        "tagline": [
            ("투자를 ", WHITE), ("네오코드", ACCENT), ("와 함께 ", WHITE),
            ("트레이딩 게임", ACCENT), ("으로 접근하세요.", WHITE),
        ],
        "top": ["삼전, 닉스는\n언제 오를까..?", "이평선은\n어디서 들어봤는데..", "세력은\n누구지..?"],
        "bottom": ["용어가\n어려워서...", "여러 책을\n봐도 헷갈리고...", "실전에\n적용하기 힘들고..."],
    },
    "en": {
        "intro": "Fundamentals? Technicals? Trading can feel overwhelming.",
        "tagline": [
            ("Approach investing as a ", WHITE), ("trading game", ACCENT),
            (" with ", WHITE), ("NEOCODE", ACCENT), (".", WHITE),
        ],
        "top": ["When will these\nstocks rise?", "Moving averages...\nwhere have I heard that?", "Who is moving\nthe market?"],
        "bottom": ["Too many\nnew terms...", "Even after many books,\nstill confusing...", "Hard to use\nin real trades..."],
    },
}


def make_copy_layer(language: str) -> tuple[Image.Image, Image.Image]:
    content = COPY[language]
    main = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(main)
    intro_size = 39 if language == "ko" else 41
    intro = content["intro"]
    while width(intro, intro_size) > W - 150:
        intro_size -= 1
    add_line(d, [(intro, WHITE)], 253, intro_size)
    tagline_size = 61 if language == "ko" else 58
    while sum(width(s, tagline_size) for s, _ in content["tagline"]) > W - 130:
        tagline_size -= 1
    add_line(d, content["tagline"], 316, tagline_size)

    notes = Image.new("RGBA", (W, H))
    nd = ImageDraw.Draw(notes)
    for value, x, y in [
        (content["top"][0], 230, 112),
        (content["top"][1], 650, 112),
        (content["top"][2], 1110, 112),
        (content["bottom"][0], 165, 420),
        (content["bottom"][1], 520, 420),
        (content["bottom"][2], 855, 420),
    ]:
        nd.multiline_text((x, y), value, fill=(*WHITE, 225), font=font(25), spacing=5)
    for x, y in [(385, 135), (820, 135), (1280, 135)]:
        nd.line([(x, y), (x + 6, y - 18)], fill=(*ACCENT, 255), width=4)
        nd.line([(x + 15, y + 2), (x + 30, y - 10)], fill=(*ACCENT, 255), width=4)
    return main, notes


random.seed(21)
deltas = [random.choice([-5, -4, -3, 2, 3, 4, 5, 6]) for _ in range(47)]
deltas += [10, 15, -4, 22, 30, -5, 36, 45, 53]
candles = []
close = 100.0
for i, delta in enumerate(deltas):
    opening = close
    close += delta
    high = max(opening, close) + random.uniform(1.5, 4.0)
    low = min(opening, close) - random.uniform(1.5, 4.0)
    volume = random.randint(9, 27) + (random.randint(15, 30) if i >= 47 else 0)
    candles.append((opening, high, low, close, volume))
minimum = min(c[2] for c in candles) - 9
maximum = max(c[1] for c in candles) + 9


def cy(value: float) -> int:
    return int(550 - (value - minimum) / (maximum - minimum) * 420)


background = Image.new("RGBA", (W, H), (*NAVY, 255))
bd = ImageDraw.Draw(background)
for y in range(H):
    mix = y / H
    bd.line((0, y, W, y), fill=(4, int(22 + 5 * mix), int(38 + 9 * mix), 255))
for y in [135, 205, 275, 345, 415, 485, 555, 622]:
    bd.line((40, y, W - 40, y), fill=(74, 101, 124, 75), width=1)
for x in range(110, W - 40, 245):
    bd.line((x, 135, x, 622), fill=(74, 101, 124, 38), width=1)


def frame(t: float, language: str, main: Image.Image, notes: Image.Image) -> Image.Image:
    image = background.copy()
    draw = ImageDraw.Draw(image, "RGBA")
    progress = min(len(candles), max(0.0, (t + .2) / 6.8 * len(candles)))
    for i, (opening, high, low, closing, volume) in enumerate(candles):
        fraction = max(0.0, min(1.0, progress - i))
        if not fraction:
            break
        x = 73 + i * 26
        shown_close = opening + (closing - opening) * fraction
        color = CORAL if closing >= opening else BLUE
        alpha = int(255 * smooth(0, 1, fraction))
        draw.line((x, cy(high), x, cy(low)), fill=(*color, alpha), width=2)
        top, bottom = sorted((cy(opening), cy(shown_close)))
        draw.rectangle((x - 8, top, x + 8, max(top + 4, bottom)), fill=(*color, alpha))
        draw.rectangle((x - 8, 610 - volume * fraction, x + 8, 610), fill=(*color, int(alpha * .78)))
    if progress >= 1:
        last = min(len(candles) - 1, int(progress - 1))
        x = 73 + last * 26
        draw.line((x, 135, x, 615), fill=(218, 233, 248, 100), width=1)
        y = cy(candles[last][3])
        radius = 4 + 2 * (1 + math.sin(t * 5))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*WHITE, 255))

    note_alpha = smooth(.8, 2.1, t)
    copy_alpha = smooth(2.0, 3.3, t)
    fade_layer(image, notes, note_alpha, rise=12)
    fade_layer(image, main, copy_alpha, rise=22)
    if t > 8.35:
        wash = int(255 * smooth(8.35, 9.0, t))
        ImageDraw.Draw(image, "RGBA").rectangle((0, 0, W, H), fill=(*NAVY, wash))
    return image.convert("RGB")


def encode(language: str) -> None:
    main, notes = make_copy_layer(language)
    poster = OUT / f"trading-game-{language}-poster.jpg"
    video = OUT / f"trading-game-{language}.mp4"
    frame(7.7, language, main, notes).save(poster, quality=91)
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for index in range(FPS * DURATION):
            process.stdin.write(frame(index / FPS, language, main, notes).tobytes())
        process.stdin.close()
        error = process.stderr.read().decode(errors="replace")
        if process.wait() != 0:
            raise RuntimeError(error)
    finally:
        if process.poll() is None:
            process.kill()
    print(video)


MW, MH = 720, 1000


def mobile_copy(language: str) -> tuple[Image.Image, Image.Image]:
    main = Image.new("RGBA", (MW, MH))
    draw = ImageDraw.Draw(main)
    content = COPY[language]
    if language == "ko":
        intro = ["기본적 분석? 기술적 분석?", "많이 헷갈리고 어렵습니다."]
        tagline = [
            [("투자를 ", WHITE), ("네오코드", ACCENT), ("와 함께", WHITE)],
            [("트레이딩 게임", ACCENT), ("으로 접근하세요.", WHITE)],
        ]
    else:
        intro = ["Fundamentals? Technicals?", "Trading can feel overwhelming."]
        tagline = [
            [("Investing as a ", WHITE), ("trading game", ACCENT)],
            [("with ", WHITE), ("NEOCODE", ACCENT), (".", WHITE)],
        ]

    for line, y in zip(intro, [300, 342]):
        size = 33 if language == "ko" else 31
        while width(line, size) > MW - 62:
            size -= 1
        x = (MW - width(line, size)) // 2
        draw.text((x, y), line, font=font(size, True), fill=(*WHITE, 255))
    for parts, y in zip(tagline, [425, 495]):
        size = 48 if language == "ko" else 46
        while sum(width(value, size) for value, _ in parts) > MW - 40:
            size -= 1
        x = (MW - sum(width(value, size) for value, _ in parts)) // 2
        for value, color in parts:
            draw.text((x, y), value, font=font(size, True), fill=(*color, 255))
            x += width(value, size)

    note_layer = Image.new("RGBA", (MW, MH))
    nd = ImageDraw.Draw(note_layer)
    for value, y in zip(content["top"], [60, 125, 190]):
        value = value.replace("\n", " ")
        size = 27 if language == "ko" else 25
        while width(value, size, bold=False) > MW - 120:
            size -= 1
        nd.line((48, y + 13, 58, y + 13), fill=(*ACCENT, 255), width=3)
        nd.text((72, y), value, font=font(size), fill=(*WHITE, 235))
    nd.line((48, 262, MW - 48, 262), fill=(*ACCENT, 185), width=3)
    for value, y in zip(content["bottom"], [603, 643, 683]):
        value = value.replace("\n", " ")
        size = 23 if language == "ko" else 21
        while width(value, size, bold=False) > MW - 120:
            size -= 1
        nd.line((48, y + 11, 58, y + 11), fill=(*ACCENT, 255), width=2)
        nd.text((72, y), value, font=font(size), fill=(*WHITE, 220))
    return main, note_layer


mobile_background = Image.new("RGBA", (MW, MH), (*NAVY, 255))
mb = ImageDraw.Draw(mobile_background)
for y in range(MH):
    mix = y / MH
    mb.line((0, y, MW, y), fill=(4, int(22 + 5 * mix), int(38 + 9 * mix), 255))
for y in [740, 790, 840, 890, 940, 970]:
    mb.line((38, y, MW - 38, y), fill=(74, 101, 124, 82), width=1)
for x in range(64, MW - 20, 125):
    mb.line((x, 735, x, 970), fill=(74, 101, 124, 55), width=1)


def mobile_frame(t: float, language: str, main: Image.Image, notes: Image.Image) -> Image.Image:
    image = mobile_background.copy()
    draw = ImageDraw.Draw(image, "RGBA")
    progress = min(len(candles), max(0.0, (t + .2) / 6.8 * len(candles)))
    for i, (opening, high, low, closing, volume) in enumerate(candles):
        fraction = max(0.0, min(1.0, progress - i))
        if not fraction:
            break
        x = 48 + i * 11
        mapped = lambda value: int(938 - (value - minimum) / (maximum - minimum) * 200)
        shown_close = opening + (closing - opening) * fraction
        color = CORAL if closing >= opening else BLUE
        alpha = int(255 * smooth(0, 1, fraction))
        draw.line((x, mapped(high), x, mapped(low)), fill=(*color, alpha), width=2)
        top, bottom = sorted((mapped(opening), mapped(shown_close)))
        draw.rectangle((x - 4, top, x + 4, max(top + 3, bottom)), fill=(*color, alpha))
        draw.rectangle((x - 4, 975 - volume * fraction, x + 4, 975), fill=(*color, int(alpha * .78)))
    fade_layer(image, notes, smooth(.7, 1.8, t), rise=10)
    fade_layer(image, main, smooth(1.8, 3.0, t), rise=18)
    if t > 8.35:
        wash = int(255 * smooth(8.35, 9.0, t))
        ImageDraw.Draw(image, "RGBA").rectangle((0, 0, MW, MH), fill=(*NAVY, wash))
    return image.convert("RGB")


def encode_mobile(language: str) -> None:
    main, notes = mobile_copy(language)
    poster = OUT / f"trading-game-mobile-{language}-poster.jpg"
    video = OUT / f"trading-game-mobile-{language}.mp4"
    mobile_frame(7.7, language, main, notes).save(poster, quality=90)
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{MW}x{MH}", "-pix_fmt", "rgb24", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for index in range(FPS * DURATION):
            process.stdin.write(mobile_frame(index / FPS, language, main, notes).tobytes())
        process.stdin.close()
        error = process.stderr.read().decode(errors="replace")
        if process.wait() != 0:
            raise RuntimeError(error)
    finally:
        if process.poll() is None:
            process.kill()
    print(video)


if __name__ == "__main__":
    encode("ko")
    encode("en")
    encode_mobile("ko")
    encode_mobile("en")
