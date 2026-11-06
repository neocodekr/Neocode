"""Generate the illustrative Signal K chart film used on the home page."""
from pathlib import Path
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = Path(__file__).parent
OUT = ROOT / "media"
OUT.mkdir(exist_ok=True)
W, H, FPS, SECONDS = 1280, 720, 24, 9
random.seed(17)

def font(size, bold=False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)

values = []
close = 100.0
# Choppy rise and fall, followed by several unmistakable long bullish candles.
deltas = [4, -3, 5, -4, 3, -6, 7, -2, 4, -5,
          6, -3, -4, 8, -2, 5, -6, 4, 3, -5,
          7, -2, 4, -6, 5, -3, 6, -2, 4, -5,
          7, -3, 5, -4, 6, -2, 4, -5, 7, -3,
          13, 16, -4, 18, 15, -3, 20, 18, 22]
for i, delta in enumerate(deltas):
    opening = close
    close = opening + delta
    high = max(opening, close) + random.uniform(1.2, 3.5)
    low = min(opening, close) - random.uniform(1.2, 3.5)
    volume = random.randint(15, 48) + (28 if i >= 40 else 0)
    values.append((opening, high, low, close, volume))

low_bound = min(v[2] for v in values) - 8
high_bound = max(v[1] for v in values) + 8

def y(v):
    return int(545 - (v - low_bound) / (high_bound - low_bound) * 390)

def frame(t):
    im = Image.new("RGB", (W, H), "#080e1b")
    d = ImageDraw.Draw(im)
    for gy in range(155, 551, 79):
        d.line((70, gy, 1210, gy), fill="#273346", width=2)
    for gx in range(80, 1210, 190):
        d.line((gx, 155, gx, 550), fill="#192638", width=1)
    d.text((74, 44), "NEOCODE / SYSTEM TRADING", fill="#ecf4ff", font=font(28, True))
    d.text((75, 91), "CANDLE SEQUENCE  /  ILLUSTRATIVE MARKET MOTION", fill="#9baec8", font=font(18, True))
    d.rounded_rectangle((1015, 49, 1205, 98), radius=24, fill="#3c1625")
    d.text((1042, 63), "LIVE MOTION", fill="#ff667c", font=font(17, True))
    progress = min(len(values), 4 + t / 5.7 * len(values))
    count = min(len(values), int(progress) + 1)
    for i, (op, hi, lo, cl, vol) in enumerate(values[:count]):
        x = 87 + i * 22
        fraction = min(1, max(0, progress - i))
        visible_close = op + (cl - op) * fraction
        color = "#ff4564" if cl >= op else "#4399ff"
        d.line((x, y(hi), x, y(lo)), fill=color, width=3)
        d.rectangle((x - 7, min(y(op), y(visible_close)), x + 7, max(y(op), y(visible_close)) + 3), fill=color)
        d.rounded_rectangle((x - 7, 627 - vol * fraction, x + 7, 627), radius=2, fill="#943447" if cl >= op else "#235797")
    if count:
        x = 87 + (count - 1) * 22
        d.line((x, 150, x, 630), fill="#456078", width=1)
        d.ellipse((x - 4, y(values[count - 1][3]) - 4, x + 4, y(values[count - 1][3]) + 4), fill="#f8e8ee")
    d.text((75, 666), "RED  /  UP        BLUE  /  DOWN", fill="#8da4bf", font=font(16, True))
    d.text((1040, 666), "00:%02d" % int(t), fill="#8da4bf", font=font(16))
    return im

frame(SECONDS).save(OUT / "stock-chart-poster.jpg", quality=90)
cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "rawvideo", "-vcodec", "rawvideo", "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "26", "-movflags", "+faststart", str(OUT / "stock-chart.mp4")]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
for index in range(FPS * SECONDS):
    proc.stdin.write(frame(index / FPS).tobytes())
proc.stdin.close()
errors = proc.stderr.read().decode(errors="replace")
if proc.wait() != 0:
    raise RuntimeError(errors)
print(OUT / "stock-chart.mp4")

# A moving crop keeps the newest candles large and visible on narrow screens.
mobile_cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "rawvideo", "-vcodec", "rawvideo", "-s", "720x1280", "-pix_fmt", "rgb24", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "28", "-movflags", "+faststart", str(OUT / "stock-chart-mobile.mp4")]
mobile_proc = subprocess.Popen(mobile_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
for index in range(FPS * SECONDS):
    t = index / FPS
    progress = min(len(values), 4 + t / 5.7 * len(values))
    newest_x = 87 + min(len(values) - 1, int(progress)) * 22
    left = max(0, min(W - 300, newest_x - 225))
    crop = frame(t).crop((left, 115, left + 300, 648)).resize((720, 1280), Image.Resampling.BICUBIC)
    mobile_proc.stdin.write(crop.tobytes())
mobile_proc.stdin.close()
mobile_errors = mobile_proc.stderr.read().decode(errors="replace")
if mobile_proc.wait() != 0:
    raise RuntimeError(mobile_errors)
print(OUT / "stock-chart-mobile.mp4")
