import random, sys
from PIL import Image, ImageDraw, ImageFilter
B, V = sys.argv[1], sys.argv[2]
def grad(w, h, c1, c2):
    m = Image.linear_gradient('L').resize((w, h))
    return Image.composite(Image.new('RGB', (w, h), c2), Image.new('RGB', (w, h), c1), m).convert('RGBA')
def glow(img, box, a, blur):
    g = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse(box, fill=(255, 255, 255, a)); img.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur)))
def sparkle(d, x, y, r, f):
    d.polygon([(x, y-r), (x+r*.22, y-r*.22), (x+r, y), (x+r*.22, y+r*.22), (x, y+r), (x-r*.22, y+r*.22), (x-r, y), (x-r*.22, y-r*.22)], fill=f)
def place(img, path, cx, bottom, h, rot=0):
    c = Image.open(path).convert('RGBA')
    if rot: c = c.rotate(rot, expand=True, resample=Image.BICUBIC)
    s = h / c.height; c = c.resize((int(c.width*s), int(c.height*s)), Image.LANCZOS)
    x = int(cx - c.width/2); sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([x+c.width*.12, bottom-14, x+c.width*.88, bottom+22], fill=(0, 40, 20, 80))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16))); img.alpha_composite(c, (x, int(bottom-c.height)))
def stage(seed, c1, c2):
    random.seed(seed); img = grad(1200, 1100, c1, c2)
    glow(img, (100, 250, 1100, 1150), 110, 120)
    d = ImageDraw.Draw(img)
    for _ in range(12): sparkle(d, random.randint(40, 1160), random.randint(40, 380), random.randint(12, 26), (255, 255, 255, 210))
    return img
# About: a family of everyday products
a = stage(5, (214, 241, 225), (123, 201, 160))
place(a, f'{B}/spray.png', 210, 980, 620, -5)
place(a, f'{V}/fan_cut.png', 500, 990, 420)
place(a, f'{B}/mic.png', 800, 990, 520)
place(a, f'{V}/juice_cut.png', 1060, 985, 540, 6)
a.convert('RGB').save(f'{B}/ms-about.jpg', quality=86)
# Contact: smaller group, more air
c = stage(9, (238, 248, 242), (180, 225, 200))
place(c, f'{B}/neck.png', 230, 980, 560, -6)
place(c, f'{V}/oil_cut.png', 590, 990, 470)
place(c, f'{V}/gun_cut.png', 960, 985, 390, 4)
c.convert('RGB').save(f'{B}/ms-contact.jpg', quality=86)
print('ok')
