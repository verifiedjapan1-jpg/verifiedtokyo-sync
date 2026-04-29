# Verified Tokyo Product Sync

t-secondhands.jp から Verified Tokyo に商品情報を自動同期するシステムです。

## 概要

- 毎日朝 6 時に t-secondhands.jp から商品データを自動取得
- Verified Tokyo のスタイルに合わせてデータを整形
- JSON ファイルとして Xserver FTP に自動アップロード
- 重複商品は自動的に排除

## セットアップ

### 1. ローカル環境での動作確認

```bash
npm install
npm run scrape    # スクレイピング実行
npm run upload    # FTP アップロード
npm run sync      # 両方実行
```

### 2. GitHub Secrets の設定

GitHub リポジトリの Settings → Secrets に以下を追加：

- `FTP_HOST`: `sv16666.xserver.jp`
- `FTP_USER`: `deploy@verifiedtokyo.com`
- `FTP_PASSWORD`: (Xserver FTP パスワード)

### 3. 自動実行スケジュール

`.github/workflows/daily-sync.yml` が毎日朝 6 時 JST に自動実行されます。

手動実行は GitHub Actions タブから "Run workflow" で可能です。

## ファイル構成

```
verifiedtokyo-sync/
├── scrape.js                      # スクレイピングメインスクリプト
├── upload.js                      # FTP アップロードスクリプト
├── package.json                   # Node.js 依存関係
├── products.json                  # 生成された商品データ
├── .github/workflows/daily-sync.yml  # GitHub Actions ワークフロー
└── README.md                      # このファイル
```

## 商品データ構造

各商品は以下の情報を含みます：

```json
{
  "id": 1,
  "name": "商品名",
  "brand": "ブランド",
  "price": 375,
  "url": "t-secondhands.jp の URL",
  "imageUrl": "メイン画像 URL",
  "productId": "商品スラッグ",
  "description": "説明文",
  "dimensions": {
    "height": "高さ",
    "width": "幅",
    "depth": "奥行き"
  },
  "specifications": {
    "color": "色",
    "material": "素材",
    "design": "デザイン",
    "hardware": "金具"
  },
  "images": ["画像URL配列"],
  "detailText": {
    "intro": "説明文",
    "dimensions": { ... },
    "description": "詳細説明",
    "specifications": ["仕様リスト"],
    "additional": "追加情報"
  }
}
```

## トラブルシューティング

### FTP アップロードが失敗する
- FTP_PASSWORD が正しく設定されているか確認
- Xserver のファイアウォール設定を確認
- `/public_html/data/` ディレクトリのパーミッションを確認

### スクレイピングが失敗する
- t-secondhands.jp のサイト構造が変更されていないか確認
- scrape.js の CSS セレクタを更新

### GitHub Actions が動作しない
- GitHub Secrets が正しく設定されているか確認
- ワークフローのログを確認

## ライセンス

© 2026 Verified Tokyo
