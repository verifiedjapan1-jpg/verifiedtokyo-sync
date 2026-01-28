# Auto-Sync Products from t-secondhands.jp

このプロジェクトは、t-secondhands.jpから商品データを自動的に同期するGitHub Actionsを使用しています。

## 🤖 自動同期の仕組み

1. **毎日午前11時（日本時間）**に自動実行
2. t-secondhands.jpから最新の商品データを取得
3. 既存データと比較して新商品/削除された商品を検出
4. 変更があれば自動的にコミット＆プッシュ

## 📁 ファイル構成

```
.github/workflows/sync-products.yml  # GitHub Actions設定
sync_products.py                     # 商品同期スクリプト
products_data.json                   # 商品データ（自動更新）
sync_log.json                        # 同期ログ
```

## 🚀 使い方

### 自動実行（推奨）
GitHubにプッシュするだけで、毎日自動的に同期されます。

```bash
git add .
git commit -m "Initial commit"
git push
```

### 手動実行

#### 方法1: GitHub Actionsで手動実行
1. GitHubリポジトリの「Actions」タブを開く
2. 「Auto-Sync Products」ワークフローを選択
3. 「Run workflow」ボタンをクリック

#### 方法2: ローカルで手動実行
```bash
# 依存関係インストール（初回のみ）
pip install playwright
playwright install chromium

# 同期スクリプト実行
python3 sync_products.py
```

## 📊 同期ログの確認

`sync_log.json`で同期履歴を確認できます：

```json
[
  {
    "timestamp": "2026-01-19T00:00:00",
    "total_products": 145,
    "added": 5,
    "removed": 2,
    "added_products": ["New Product 1", "New Product 2"],
    "removed_products": ["Old Product 1"]
  }
]
```

## ⚙️ カスタマイズ

### 同期頻度の変更
`.github/workflows/sync-products.yml`の`cron`設定を変更：

```yaml
schedule:
  - cron: '0 2 * * *'  # 毎日午前2時（UTC） = 午前11時（JST）
  # - cron: '0 */6 * * *'  # 6時間ごと
  # - cron: '0 0 * * 1'    # 毎週月曜日
```

### 通知の追加（オプション）
Slack通知を追加する場合：

1. Slack Webhook URLを取得
2. GitHub Secretsに`SLACK_WEBHOOK_URL`を追加
3. `sync_products.py`に通知コード追加

## 🔧 トラブルシューティング

### GitHub Actionsが失敗する場合

1. **Actions」タブで詳細ログを確認**
2. **原因：** Playwrightのインストールエラー
   - **解決：** ワークフローファイルを確認

3. **原因：** プッシュ権限エラー
   - **解決：** リポジトリ設定 → Actions → General → 「Read and write permissions」を有効化

### ローカル実行でエラーが出る場合

```bash
# Playwright再インストール
pip uninstall playwright
pip install playwright
playwright install chromium
```

## 📝 開発者向け情報

### スクリプトの動作

1. `fetch_latest_products()` - Playwrightでスクレイピング
2. `compare_products()` - 新旧データの差分検出
3. `update_json_file()` - JSONファイル更新
4. `log_sync()` - ログ記録

### テスト実行

```bash
# ドライラン（ファイル更新なし）
python3 sync_products.py --dry-run  # TODO: 実装予定
```

## 🌟 次のステップ

- [ ] HTMLファイルの自動更新機能追加
- [ ] Slack/Email通知機能追加
- [ ] 画像の自動ダウンロード機能追加

---

**Last Updated:** 2026-01-19
