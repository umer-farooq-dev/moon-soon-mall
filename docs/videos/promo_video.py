"""Render a 720x1280 vertical promo video for one product from its cutout + lifestyle photo.

usage: promo_video.py <dir> <key> "<title>" <price> <compare> "<f1|f2|f3>"
"""
import math, subprocess, sys
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

D, KEY, TITLE, PRICE, WAS, FEATS = sys.argv[1:7]
PRICE, WAS = int(PRICE), int(WAS)
FEATS = FEATS.split('|')
W, H, FPS = 720, 1280, 30
T1, T2, T3 = 4.0, 4.5, 4.0          # scene lengths
X = 0.4                              # crossfade
TOTAL = T1 + T2 + T3
GREEN_D, GREEN_L = (14, 74, 46), (123, 201, 160)
CREAM, ORANGE, WHITE = (255, 245, 196), (240, 138, 62), (255, 255, 255)

bold = lambda s: ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', s)
reg = lambda s: ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', s)
ease = lambda t: 1 - (1 - min(max(t, 0), 1)) ** 3


def money(v):
    return 'Rs ' + f'{v:,}'


def grad(c1, c2):
    m = Image.linear_gradient('L').resize((W, H))
    return Image.composite(Image.new('RGB', (W, H), c2), Image.new('RGB', (W, H), c1), m).convert('RGBA')


def glow(img, box, a, blur):
    g = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse(box, fill=(255, 255, 255, a))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur)))


def wrap(text, font, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if font.getlength(t) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def text_center(img, y, text, font, fill, alpha=1.0, shadow=True):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for line in wrap(text, font, W - 80):
        w = font.getlength(line)
        if shadow:
            d.text(((W - w) / 2 + 3, y + 3), line, font=font, fill=(0, 30, 15, 110))
        d.text(((W - w) / 2, y), line, font=font, fill=fill)
        y += font.size * 1.2
    if alpha < 1:
        layer.putalpha(layer.split()[3].point(lambda v: int(v * alpha)))
    img.alpha_composite(layer)
    return y


def pill(img, cx, y, text, font, bg, fg, alpha=1.0):
    w = font.getlength(text) + 44
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([cx - w / 2, y, cx + w / 2, y + font.size + 26], radius=40, fill=bg)
    d.text((cx - w / 2 + 22, y + 9), text, font=font, fill=fg)
    if alpha < 1:
        layer.putalpha(layer.split()[3].point(lambda v: int(v * alpha)))
    img.alpha_composite(layer)


cut = Image.open(f'{D}/{KEY}_cut.png').convert('RGBA')
life = ImageOps.exif_transpose(Image.open(f'{D}/{KEY}_l.jpg')).convert('RGB')
bg1 = grad(GREEN_L, GREEN_D)
glow(bg1, (60, 380, 660, 1000), 80, 90)
bg3 = grad((238, 248, 242), (207, 230, 216))
glow(bg3, (80, 260, 640, 820), 120, 80)


def product(img, cx, cy, size, t, shadow=True):
    s = size / max(cut.size)
    c = cut.resize((int(cut.width * s), int(cut.height * s)), Image.LANCZOS)
    x, y = int(cx - c.width / 2), int(cy - c.height / 2)
    if shadow:
        sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([x + c.width * .15, y + c.height - 6, x + c.width * .85, y + c.height + 30], fill=(0, 30, 15, 90))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(c, (x, y))


def scene1(t):
    img = bg1.copy()
    k = t / T1
    product(img, W / 2, 700 + 14 * math.sin(t * 2.2), 470 + 90 * ease(k * 1.3), t)
    pill(img, W / 2, 150, 'NEW AT MOONSOONMALL', bold(26), CREAM, GREEN_D, ease(t / 0.6))
    text_center(img, 230, TITLE, bold(64), WHITE, ease((t - 0.3) / 0.7))
    return img


_bh = int(W * life.height / life.width) if life.width / life.height > W / H else H
_blur = ImageOps.fit(life, (W, H)).filter(ImageFilter.GaussianBlur(28)).convert('RGBA')
_blur.alpha_composite(Image.new('RGBA', (W, H), (8, 40, 24, 150)))


def scene2(t):
    k = t / T2
    img = _blur.copy()
    cw = int(640 * (1.0 + 0.05 * k))
    ch = min(int(cw * life.height / life.width), 660)
    card = ImageOps.fit(life, (cw, ch)).convert('RGBA')
    m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, cw, ch], radius=36, fill=255)
    card.putalpha(m)
    x, y = (W - cw) // 2, 110 + (660 - ch) // 2 - int((cw - 640) / 2)
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x + 8, y + 14, x + cw + 8, y + ch + 14], radius=36, fill=(0, 0, 0, 90))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    img.alpha_composite(card, (x, y))
    y0 = 830
    for i, f in enumerate(FEATS[:3]):
        a = ease((t - 0.4 - i * 0.7) / 0.5)
        if a <= 0:
            continue
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        y = y0 + i * 112 + int((1 - a) * 30)
        d.rounded_rectangle([50, y, W - 50, y + 88], radius=44, fill=(255, 255, 255, 235))
        d.ellipse([68, y + 18, 120, y + 70], fill=(46, 139, 87))
        d.line([(82, y + 45), (92, y + 56), (108, y + 33)], fill=WHITE, width=6)
        fnt = bold(30)
        line = wrap(f, fnt, W - 210)[0]
        d.text((140, y + 24), line, font=fnt, fill=(31, 107, 69))
        layer.putalpha(layer.split()[3].point(lambda v: int(v * a)))
        img.alpha_composite(layer)
    return img


def scene3(t):
    img = bg3.copy()
    product(img, W / 2, 470 + 8 * math.sin(t * 2.5), 470, t)
    pct = round((WAS - PRICE) * 100 / WAS) if WAS > PRICE else 0
    a = ease(t / 0.6)
    if pct:
        pill(img, W / 2, 770, f'SAVE {pct}%', bold(30), ORANGE, WHITE, a)
    text_center(img, 845, money(PRICE), bold(92), (31, 107, 69), a, shadow=False)
    if WAS > PRICE:
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        f = reg(40); s = money(WAS); w = f.getlength(s)
        d.text(((W - w) / 2, 965), s, font=f, fill=(107, 124, 114))
        d.line([((W - w) / 2 - 4, 991), ((W + w) / 2 + 4, 991)], fill=(107, 124, 114), width=4)
        layer.putalpha(layer.split()[3].point(lambda v: int(v * a)))
        img.alpha_composite(layer)
    b = ease((t - 0.7) / 0.6)
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rounded_rectangle([90, 1056, W - 84, 1146], radius=30, fill=(14, 74, 46))
    d.rounded_rectangle([84, 1050, W - 90, 1140], radius=30, fill=(46, 139, 87))
    f = bold(36); s = 'ORDER NOW'; d.text(((W - f.getlength(s)) / 2 - 3, 1070), s, font=f, fill=WHITE)
    f2 = bold(26); s2 = 'Cash on Delivery all over Pakistan'
    d.text(((W - f2.getlength(s2)) / 2, 1172), s2, font=f2, fill=(31, 107, 69))
    layer.putalpha(layer.split()[3].point(lambda v: int(v * b)))
    img.alpha_composite(layer)
    return img


def frame(t):
    if t < T1 - X / 2:
        return scene1(t)
    if t < T1 + X / 2:
        k = (t - (T1 - X / 2)) / X
        return Image.blend(scene1(t), scene2(t - T1 + X / 2), k)
    if t < T1 + T2 - X / 2:
        return scene2(t - T1 + X / 2)
    if t < T1 + T2 + X / 2:
        k = (t - (T1 + T2 - X / 2)) / X
        return Image.blend(scene2(t - T1 + X / 2), scene3(t - T1 - T2 + X / 2), k)
    return scene3(t - T1 - T2 + X / 2)


out = f'{D}/ms-video-{KEY}.mp4'
cmd = [imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
       '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
       '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
n = int(TOTAL * FPS)
for i in range(n):
    p.stdin.write(frame(i / FPS).convert('RGB').tobytes())
p.stdin.close(); p.wait()
frame(1.5).convert('RGB').save(f'{D}/prev-{KEY}-1.jpg', quality=70)
frame(T1 + 3).convert('RGB').save(f'{D}/prev-{KEY}-2.jpg', quality=70)
frame(TOTAL - 0.5).convert('RGB').save(f'{D}/prev-{KEY}-3.jpg', quality=70)
print(out, p.returncode)
