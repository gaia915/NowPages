# 🪐 NowPages - プラネタリウム最新イベント自動収集・生成システム

全国の主要プラネタリウム（コニカミノルタ直営各館、日本科学未来館、全国科学館・イベント情報）から最新の上映プログラム・特別企画展・コラボイベント情報を定期的に自動収集し、宇宙・星空をモチーフにしたモダンなWebページ（HTML）とMarkdownファイルを自動生成するシステムです。

---

## ✨ 主な機能と特徴

1. **マルチソースからの自動収集（スクレイパー）**:
   - **ウォーカープラス（全国プラネタリウム・天体観測一覧）**: 全国の科学館・プラネタリウムの特別展、生解説上映、観望会など最新イベントを網羅。
   - **コニカミノルタプラネタリウム（公式）**: プラネタリアTOKYO（有楽町）、満天（池袋）、天空（押上）、プラネタリアYOKOHAMA、満天NAGOYAの上映プログラム・アーティストコラボ・限定フェア情報。
   - **日本科学未来館（ドームシアターガイア）**: 3Dドーム映像作品、科学特別上映プログラム。
2. **宇宙・星空をテーマにした洗練されたWeb UI (`dist/index.html`)**:
   - 深い夜空と星の瞬き（Starfieldアニメーション）、ネオンアクセントのダークテーマ。
   - **リアルタイムキーワード検索**: 作品名、アーティスト名、会場名、エリアで即座に絞り込み。
   - **エリア別フィルター**: 東京、関東全域、中部・愛知、近畿・関西、全国その他。
   - **ステータスフィルター**: 「開催・上映中」「注目・NEW」。
   - **お気に入り（ブックマーク）機能**: 行きたいイベントを星アイコンで保存（ブラウザのLocalStorageに保存）。
   - **統計ダッシュボード**: 掲載総数、開催中数、対象施設数、更新日時の可視化。
3. **Markdown (`dist/events.md`) & JSON (`dist/events.json`) 出力**:
   - ブログやNotion、GitHubのREADMEなどにそのまま貼り付けて利用可能。
4. **定期自動更新（GitHub Actions & ローカルバッチ）**:
   - **GitHub Actions**: 毎日朝6時（JST）に自動で最新データを取得し、GitHub Pagesに完全自動デプロイ。
   - **Windowsバッチ (`run.bat`)**: ダブルクリックするだけで最新情報を取得し、ブラウザで自動表示。

---

## 📁 ディレクトリ構成

```text
NowPages/
├── .github/
│   └── workflows/
│       └── update_events.yml     # GitHub Actions定期自動更新＆デプロイ
├── data/
│   └── events_cache.json         # 収集データのローカルキャッシュ
├── dist/                         # 生成された公開用ファイル
│   ├── index.html                # メインWebページ
│   ├── events.md                 # Markdown形式の一覧
│   ├── events.json               # 構造化JSONデータ
│   └── assets/                   # CSS・JavaScript
├── src/
│   ├── __init__.py
│   ├── models.py                 # イベントデータモデル定義
│   ├── scraper.py                # スクレイパー（Walkerplus, コニカミノルタ, 未来館等）
│   └── generator.py              # Jinja2によるHTML/Markdownページ生成器
├── templates/
│   ├── index.html.jinja          # Webページテンプレート
│   ├── events.md.jinja           # Markdownテンプレート
│   └── assets/                   # スタイルシート・スクリプト原本
├── requirements.txt              # Python依存ライブラリ
├── main.py                       # 一括実行CLIエントリーポイント
├── run.bat                       # Windowsワンクリック実行バッチ
└── README.md
```

---

## 🚀 クイックスタート（ローカル実行）

### 1. 依存ライブラリのインストール
```bash
pip install -r requirements.txt
```

### 2. イベント収集＆ページ生成
```bash
python main.py --open
```
`--open` オプションを付けると、生成完了後にブラウザで自動的に生成されたページ（`dist/index.html`）が開きます。

### 3. Windowsでのワンクリック実行
`run.bat` をダブルクリックするだけで、自動的に収集とページ生成が行われ、ブラウザが開きます。

---

## ☁️ GitHub Actionsによる完全自動化設定

本リポジトリをGitHubにプッシュすることで、クラウド上で毎日自動実行され、GitHub Pagesで無料公開できます。

1. GitHubリポジトリの **Settings** > **Pages** に移動します。
2. **Build and deployment** の **Source** を `GitHub Actions` に設定します。
3. これにより、`.github/workflows/update_events.yml` が毎日自動で最新のプラネタリウムイベントを取得し、Webページを最新状態に更新します（Actionsタブから手動で「Run workflow」を実行することも可能です）。

---

## ⚙️ コマンドラインオプション (`main.py`)

| オプション | 説明 |
| :--- | :--- |
| `--output-dir <dir>` | 生成先ディレクトリを指定（デフォルト: `dist`） |
| `--use-cache` | 前回収集した `data/events_cache.json` を使って瞬時にページを再生成 |
| `--open` | 生成完了後に既定のWebブラウザで開く |
