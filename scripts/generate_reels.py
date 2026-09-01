#!/usr/bin/env python3
"""
VERIFIED TOKYO - Reel Batch Generator (GitHub Actions用)

products_data.json から指定IDの商品画像をダウンロードし、
make_reel.py で9:16スライドショー動画を生成する。

env:
  PRODUCT_IDS  カンマ区切りの商品ID。未指定なら DEFAULT_IDS を使用
"""
import os, json, requests
from make_reel import render, parse_product

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "products_data.json")
OUT = os.path.join(HERE, "..", "reels_out")
TMP = os.path.join(HERE, "..", "_tmp_images")

# 初期12選定（picks.json と同一）。workflow_dispatch の product_ids 指定で上書き可
DEFAULT_IDS = [635, 187, 545, 921, 960, 149, 644, 275, 397, 464, 79, 784]


def download(url, path):
    r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)


def main():
    ids_env = os.environ.get("PRODUCT_IDS", "").strip()
    ids = [int(x) for x in ids_env.split(",") if x.strip()] if ids_env else DEFAULT_IDS

    data = json.load(open(DATA))
    by_id = {p["id"]: p for p in data}

    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)

    for pid in ids:
        rec = by_id.get(pid)
        if not rec:
            print(f"  ! {pid}: products_data.json に見つかりません")
            continue

        urls = [rec["imageUrl"]] + [u for u in rec.get("images", []) if u != rec["imageUrl"]]
        urls = urls[:5]
        local_paths = []
        pdir = os.path.join(TMP, str(pid))
        os.makedirs(pdir, exist_ok=True)
        for i, u in enumerate(urls):
            lp = os.path.join(pdir, f"{i}.jpg")
            try:
                download(u, lp)
                local_paths.append(lp)
            except Exception as e:
                print(f"  ! {pid} image {i}: {e}")

        if not local_paths:
            print(f"  ! {pid}: 画像取得0枚のためスキップ")
            continue

        try:
            # cert=None -> Entrupyはテキスト表示のみ（画像は使わない）
            render(parse_product(rec), local_paths, None,
                   os.path.join(OUT, f"vt_{pid}.mp4"))
        except Exception as e:
            print(f"  ! {pid}: render失敗 {e}")

    print(f"\n完了。{OUT}/ を確認してください。")


if __name__ == "__main__":
    main()
