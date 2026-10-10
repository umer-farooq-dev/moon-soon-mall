"""Hero banners (desktop 2400x1000, mobile 1100x1400): sky/green scene, clouds, podium, product cutouts.
Left side (desktop) / top (mobile) is kept calm for the theme's text overlay."""
import random, sys
from PIL import Image, ImageDraw, ImageFilter
B, V, OUT = sys.argv[1:4]


def vgrad(w, h, top, bottom):
    m = Image.linear_gradient('L').resize((w, h))
    return Image.composite(Image.new('RGB', (w, h), bottom), Image.new('RGB', (w, h), top), m).convert('RGBA')


def soft(img, draw_fn, rgb, alpha, blur):
    m = Image.new('L', img.size, 0)
    draw_fn(ImageDraw.Draw(m))
    m = m.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: v * alpha // 255)
    layer = Image.new('RGBA', img.size, rgb + (0,))
    layer.putalpha(m)
    img.alpha_composite(layer)


def blob(img, box, rgba, blur):
    soft(img, lambda d: d.ellipse(box, fill=255), rgba[:3], rgba[3], blur)


def cloud(img, cx, cy, s):
    def draw(d):
        for dx, dy, r in [(-1.1, .25, .55), (-.45, -.15, .75), (.35, -.3, .85), (1.05, .1, .6), (0, .35, .7)]:
            x, y, rr = cx + dx * s, cy + dy * s, r * s
            d.ellipse([x - rr, y - rr * .8, x + rr, y + rr * .8], fill=255)
    soft(img, draw, (255, 255, 255), 240, s * .07)


def sparkle(d, x, y, r, f):
    d.polygon([(x, y - r), (x + r * .22, y - r * .22), (x + r, y), (x + r * .22, y + r * .22),
               (x, y + r), (x - r * .22, y + r * .22), (x - r, y), (x - r * .22, y - r * .22)], fill=f)


def podium(img, cx, top, w, h, face, side):
    g = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    eh = w * 0.18
    d.rectangle([cx - w / 2, top + eh / 2, cx + w / 2, top + h], fill=side)
    d.ellipse([cx - w / 2, top + h - eh / 2, cx + w / 2, top + h + eh / 2], fill=side)
    d.ellipse([cx - w / 2, top, cx + w / 2, top + eh], fill=face)
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([cx - w * .6, top + h + eh * .1, cx + w * .6, top + h + eh * .9], fill=(0, 40, 60, 70))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(25)))
    img.alpha_composite(g)
    return top + eh / 2


def place(img, path, cx, bottom, h, rot=0):
    c = Image.open(path).convert('RGBA')
    if rot:
        c = c.rotate(rot, expand=True, resample=Image.BICUBIC)
    s = h / c.height
    c = c.resize((int(c.width * s), int(c.height * s)), Image.LANCZOS)
    x = int(cx - c.width / 2)
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([x + c.width * .1, bottom - 12, x + c.width * .9, bottom + 16], fill=(0, 30, 40, 110))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    img.alpha_composite(c, (x, int(bottom - c.height)))


def scene(w, h, kind, seed, layout):
    random.seed(seed)
    if kind == 'sky':
        img = vgrad(w, h, (96, 170, 236), (196, 228, 250))
        blob(img, (int(w * .05), -int(h * .3), int(w * .55), int(h * .5)), (255, 250, 220, 150), 160)
        face, side = (250, 252, 255, 255), (214, 230, 244, 255)
        spark = (255, 255, 255, 230)
    else:
        img = vgrad(w, h, (46, 139, 87), (168, 222, 190))
        blob(img, (int(w * .1), -int(h * .3), int(w * .6), int(h * .5)), (255, 250, 220, 110), 160)
        face, side = (255, 255, 255, 255), (222, 240, 229, 255)
        spark = (255, 245, 196, 235)
    return img, face, side, spark


def deco(img, kind, spots):
    for cx, cy, s in spots:
        if kind == 'sky':
            cloud(img, cx, cy, s)
        else:
            blob(img, (cx - s, cy - s, cx + s, cy + s), (255, 255, 255, 60), s * .25)


def build(kind, items, out, seed):
    # desktop
    W, H = 2400, 1000
    img, face, side, spark = scene(W, H, kind, seed, 'd')
    deco(img, kind, [(1250, 860, 150), (2250, 820, 190), (1750, 960, 220), (2050, 180, 90), (1450, 140, 70)])
    d = ImageDraw.Draw(img)
    for _ in range(14):
        sparkle(d, random.randint(1150, 2350), random.randint(40, 600), random.randint(12, 30), spark)
    top = podium(img, 1760, 690, 900, 170, face, side)
    for path, dx, hh, rot in items:
        place(img, path, 1760 + dx, top + 40, hh, rot)
    deco(img, kind, [(1150, 1010, 170), (2350, 1000, 200)])
    img.convert('RGB').save(f'{OUT}/{out}.jpg', quality=85)
    # mobile
    W, H = 1100, 1400
    img, face, side, spark = scene(W, H, kind, seed + 1, 'm')
    deco(img, kind, [(150, 1330, 160), (950, 1300, 190), (850, 160, 80)])
    d = ImageDraw.Draw(img)
    for _ in range(10):
        sparkle(d, random.randint(40, 1060), random.randint(520, 760), random.randint(10, 24), spark)
    top = podium(img, 550, 1150, 900, 150, face, side)
    for path, dx, hh, rot in items:
        place(img, path, 550 + dx * 1.0, top + 36, hh * 1.12, rot)
    deco(img, kind, [(80, 1440, 150), (1050, 1440, 170)])
    img.convert('RGB').save(f'{OUT}/{out}-mobile.jpg', quality=85)


build('sky', [(f'{B}/neck.png', -260, 470, -8), (f'{V}/fan_cut.png', 90, 430, 0)], 'ms-hero-cooling', 3)
build('green', [(f'{B}/spray.png', -280, 520, -6), (f'{V}/juice_cut.png', 20, 470, 0), (f'{V}/oil_cut.png', 290, 400, 0)], 'ms-hero-kitchen', 8)
print('ok')
