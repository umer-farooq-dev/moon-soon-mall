import os, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
D = sys.argv[1]
def grad(w, h, c1, c2):
    m = Image.linear_gradient('L').rotate(90).resize((w, h))  # left->right
    return Image.composite(Image.new('RGB', (w, h), c1), Image.new('RGB', (w, h), c2), m)
def sparkle(d, x, y, r, f):
    d.polygon([(x, y-r), (x+r*.22, y-r*.22), (x+r, y), (x+r*.22, y+r*.22), (x, y+r), (x-r*.22, y+r*.22), (x-r, y), (x-r*.22, y-r*.22)], fill=f)
def glow(img, box, a, blur):
    g = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse(box, fill=(255, 255, 255, a))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur)))
def place(img, name, cx, bottom, h, rot=0):
    c = Image.open(f'{D}/{name}.png')
    if rot: c = c.rotate(rot, expand=True, resample=Image.BICUBIC)
    s = h / c.height; c = c.resize((int(c.width*s), int(c.height*s)), Image.LANCZOS)
    x = int(cx - c.width/2); sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([x+c.width*.12, bottom-16, x+c.width*.88, bottom+20], fill=(0, 30, 15, 110))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16))); img.alpha_composite(c, (x, int(bottom-c.height)))
random.seed(11)
W, H = 2400, 1000
img = grad(W, H, (16, 84, 52), (110, 196, 150)).convert('RGBA')
glow(img, (-150, 120, 1050, 1150), 70, 120)
glow(img, (1500, -300, 2700, 600), 25, 150)
d = ImageDraw.Draw(img)
for _ in range(10): sparkle(d, random.randint(60, 950), random.randint(60, 940), random.randint(14, 30), (255, 245, 196, 230))
place(img, 'spray', 250, 900, 600, -6)
place(img, 'mic', 560, 910, 520)
place(img, 'neck', 860, 880, 470, 8)
f = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 104)
lab = Image.new('RGBA', (900, 200), (0, 0, 0, 0)); ld = ImageDraw.Draw(lab)
ld.text((14, 34), 'new arrivals', font=f, fill=(0, 50, 25, 90)); ld.text((8, 26), 'new arrivals', font=f, fill=(255, 245, 196, 255))
img.alpha_composite(lab.rotate(7, expand=True, resample=Image.BICUBIC), (120, 40))
img.convert('RGB').save(f'{D}/ms-new-arrivals-bg.jpg', quality=86)
m = grad(900, 1300, (16, 84, 52), (110, 196, 150)).convert('RGBA'); glow(m, (-200, 700, 700, 1500), 50, 120)
dm = ImageDraw.Draw(m)
for _ in range(9): sparkle(dm, random.randint(30, 870), random.randint(30, 1270), random.randint(12, 24), (255, 245, 196, 200))
m.convert('RGB').save(f'{D}/ms-new-arrivals-bg-mobile.jpg', quality=86)
print('ok')
