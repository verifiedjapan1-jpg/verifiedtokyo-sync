#!/usr/bin/env python3
"""
VERIFIED TOKYO - Reel Generator
商品画像 -> 9:16 縦型スライドショー動画 (TikTok / IG Reels)

usage:
  python3 make_reel.py --product 635 --images img1.jpg img2.jpg ... --cert entrupy.jpg
  python3 make_reel.py --batch picks.json --imgdir ./images --cert entrupy.jpg
"""
import os, sys, json, math, subprocess, argparse
from PIL import Image, ImageDraw, ImageFont

# ---------- brand tokens (ig_grid_spec.docx 準拠) ----------
W, H, FPS = 1080, 1920, 24
BG      = (248, 247, 245)   # #F8F7F5 cool ivory
INK     = (10, 10, 10)      # #0A0A0A
ACCENT  = (184, 160, 144)   # #B8A090 rose gold
MUTED   = (138, 133, 128)
DARK_BG = (10, 10, 10)

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
SERIF = os.path.join(FONT_DIR, "CormorantGaramond.ttf")
SANS  = os.path.join(FONT_DIR, "Jost.ttf")

# timing (seconds)
T_INTRO, T_SLIDE, T_FADE, T_OUTRO = 1.6, 2.6, 0.45, 3.2
MAX_SLIDES = 5


def font(path, size, weight=None):
    f = ImageFont.truetype(path, size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def tracked(draw, xy, text, fnt, fill, track=0, anchor="mm"):
    """レタースペーシング付きテキスト描画（PILに字間機能がないため自前実装）"""
    if not text:
        return
    widths = [draw.textlength(c, font=fnt) for c in text]
    total = sum(widths) + track * (len(text) - 1)
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=fnt, fill=fill, anchor="l" + anchor[1])
        x += w + track


def fit_cover(im, bw, bh, zoom=1.0):
    """cover でボックスに収め、zoom 倍に拡大して中央クロップ"""
    tw, th = int(bw * zoom), int(bh * zoom)
    r = max(tw / im.width, th / im.height)
    nw, nh = max(1, int(im.width * r + 0.5)), max(1, int(im.height * r + 0.5))
    im2 = im.resize((nw, nh), Image.LANCZOS)
    l, t = (nw - tw) // 2, (nh - th) // 2
    im2 = im2.crop((l, t, l + tw, t + th))
    l2, t2 = (tw - bw) // 2, (th - bh) // 2
    return im2.crop((l2, t2, l2 + bw, t2 + bh))


def ease(t):
    """easeInOutSine — 直線的なズームは安っぽく見えるため"""
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


# ---------- frame builders ----------
IMG_BOX = (90, 300, 990, 1420)   # 商品画像の描画領域


def chrome(canvas, p):
    """全フレーム共通の枠（ロゴ・商品情報・フッター）"""
    d = ImageDraw.Draw(canvas)
    tracked(d, (W // 2, 132), "VERIFIED TOKYO", font(SANS, 34, 400), INK, track=13)
    d.line([(W // 2 - 60, 176), (W // 2 + 60, 176)], fill=ACCENT, width=1)

    tracked(d, (W // 2, 1530), p["brand"].upper(), font(SERIF, 74, 500), INK, track=5)

    model = p.get("model") or ""
    if model:
        f = font(SANS, 29, 300)
        while d.textlength(model, font=f) > 900 and len(model) > 8:
            model = model[:-4] + "…"
        d.text((W // 2, 1602), model, font=f, fill=MUTED, anchor="mm")

    tracked(d, (W // 2, 1690), f"$ {p['price']:,.0f}", font(SERIF, 62, 500), ACCENT, track=3)

    d.line([(90, 1790), (990, 1790)], fill=(226, 222, 216), width=1)
    tracked(d, (W // 2, 1836), "ENTRUPY CERTIFIED   ·   SHIPPED FROM TOKYO",
            font(SANS, 22, 400), MUTED, track=5)
    return canvas


def frame_slide(im, p, t):
    """t: 0->1 のスライド内進行度。ゆっくりズーム"""
    c = Image.new("RGB", (W, H), BG)
    bw, bh = IMG_BOX[2] - IMG_BOX[0], IMG_BOX[3] - IMG_BOX[1]
    c.paste(fit_cover(im, bw, bh, 1.0 + 0.055 * ease(t)), (IMG_BOX[0], IMG_BOX[1]))
    return chrome(c, p)


def frame_intro(p):
    c = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(c)
    tracked(d, (W // 2, 820), "VERIFIED", font(SERIF, 132, 400), INK, track=18)
    tracked(d, (W // 2, 940), "TOKYO", font(SERIF, 132, 400), INK, track=18)
    d.line([(W // 2 - 90, 1030), (W // 2 + 90, 1030)], fill=ACCENT, width=1)
    tracked(d, (W // 2, 1096), "PRE-OWNED LUXURY · AUTHENTICATED",
            font(SANS, 26, 400), MUTED, track=7)
    return c


def frame_outro(cert):
    c = Image.new("RGB", (W, H), DARK_BG)
    d = ImageDraw.Draw(c)
    if cert is not None:
        box = (240, 520, 840, 1120)
        c.paste(fit_cover(cert, box[2] - box[0], box[3] - box[1]), (box[0], box[1]))
    tracked(d, (W // 2, 1290), "EVERY ITEM", font(SANS, 28, 300), (150, 146, 141), track=9)
    tracked(d, (W // 2, 1390), "ENTRUPY CERTIFIED", font(SERIF, 72, 500), (255, 255, 255), track=5)
    d.line([(W // 2 - 80, 1470), (W // 2 + 80, 1470)], fill=ACCENT, width=1)
    tracked(d, (W // 2, 1560), "verifiedtokyo.com", font(SANS, 34, 400), ACCENT, track=5)
    tracked(d, (W // 2, 1650), "DM FOR CONDITION REPORT", font(SANS, 24, 400), (150, 146, 141), track=6)
    return c


# ---------- render ----------
def render(product, image_paths, cert_path, out_path, silent=False):
    imgs = []
    for p in image_paths[:MAX_SLIDES]:
        try:
            imgs.append(Image.open(p).convert("RGB"))
        except Exception as e:
            print(f"  ! skip {p}: {e}")
    if not imgs:
        raise RuntimeError("有効な画像が0枚です")

    cert = None
    if cert_path and os.path.exists(cert_path):
        cert = Image.open(cert_path).convert("RGB")

    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path],
        stdin=subprocess.PIPE)

    def push(im):
        ff.stdin.write(im.tobytes())

    nfade = int(T_FADE * FPS)

    # intro
    intro = frame_intro(product)
    for i in range(int(T_INTRO * FPS)):
        push(intro)

    # slides
    prev_tail = intro
    for idx, im in enumerate(imgs):
        n = int(T_SLIDE * FPS)
        frames = [frame_slide(im, product, i / max(1, n - 1)) for i in range(n)]
        for i in range(nfade):                      # 前カットからクロスフェード
            push(Image.blend(prev_tail, frames[i], (i + 1) / nfade))
        for f in frames[nfade:]:
            push(f)
        prev_tail = frames[-1]

    # outro
    outro = frame_outro(cert)
    for i in range(nfade):
        push(Image.blend(prev_tail, outro, (i + 1) / nfade))
    for i in range(int(T_OUTRO * FPS) - nfade):
        push(outro)

    ff.stdin.close()
    ff.wait()
    if not silent:
        dur = T_INTRO + len(imgs) * T_SLIDE + T_OUTRO
        print(f"  ✓ {os.path.basename(out_path)}  ({dur:.1f}s / {len(imgs)}枚)")
    return out_path


def parse_product(rec):
    """products_data.json のレコードから表示用フィールドを組み立てる"""
    name, brand = rec["name"], rec.get("brand", "")
    model = name
    for pre in (brand, "Authentic", "CHRISTIAN DIOR", "YVES SAINT LAURENT"):
        if pre and model.upper().startswith(pre.upper()):
            model = model[len(pre):].strip()
    parts = model.split()
    if parts and len(parts[-1]) <= 10 and any(ch.isdigit() for ch in parts[-1]):
        parts = parts[:-1]                      # 末尾の管理番号(HE371等)を除去
    return {"brand": brand, "model": " ".join(parts).strip(),
            "price": rec.get("price_usd_final") or rec.get("price") or 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", help="picks.json / products_data.json")
    ap.add_argument("--product", type=int, help="単体生成する商品ID")
    ap.add_argument("--imgdir", default="./images", help="{id}/ 配下に画像を置く")
    ap.add_argument("--images", nargs="*", help="単体生成時の画像パス")
    ap.add_argument("--cert", default="entrupy.jpg")
    ap.add_argument("--out", default="./out")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    if a.product and a.images:
        rec = {"name": f"ID {a.product}", "brand": "VERIFIED", "price_usd_final": 0}
        if a.batch:
            data = json.load(open(a.batch))
            rec = next(r for r in data if r.get("id") == a.product)
        render(parse_product(rec), a.images, a.cert,
               os.path.join(a.out, f"vt_{a.product}.mp4"))
        return

    data = json.load(open(a.batch))
    for rec in data:
        pid = rec.get("id")
        d = os.path.join(a.imgdir, str(pid))
        if not os.path.isdir(d):
            print(f"  - {pid}: 画像フォルダなし ({d})")
            continue
        paths = [os.path.join(d, f) for f in sorted(os.listdir(d))
                 if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
        try:
            render(parse_product(rec), paths, a.cert, os.path.join(a.out, f"vt_{pid}.mp4"))
        except Exception as e:
            print(f"  ! {pid}: {e}")


if __name__ == "__main__":
    main()
