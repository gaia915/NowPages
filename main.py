import argparse
import os
import sys
import json
import webbrowser
from datetime import datetime

# srcパスの追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Windows CP932環境でのエンコードエラー対策
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from src.scraper import PlanetariumAggregator
from src.generator import PageGenerator
from src.models import Event
from src.history import HistoryManager

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "events_cache.json")

def main():
    parser = argparse.ArgumentParser(description="プラネタリウム最新イベント ページ生成CLI")
    parser.add_argument("--output-dir", default="dist", help="出力先ディレクトリ (デフォルト: dist)")
    parser.add_argument("--use-cache", action="store_true", help="前回のキャッシュデータを使用してページ再生成")
    parser.add_argument("--open", action="store_true", help="生成後にブラウザで開く")
    args = parser.parse_args()

    print("=" * 60)
    print(" [PLANETARIUM] プラネタリウム最新イベント ページジェネレーター")
    print("=" * 60)

    events = []

    if args.use_cache and os.path.exists(CACHE_FILE):
        print(f"[CACHE] キャッシュデータを読み込んでいます: {CACHE_FILE}")
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            events = [Event(**item) for item in data]
        print(f"[OK] キャッシュから {len(events)} 件のイベントを復元しました。")
    else:
        print("[FETCH] 全国のプラネタリウム最新イベントを収集しています...")
        aggregator = PlanetariumAggregator()
        events = aggregator.aggregate()

    # 履歴マネージャーによる初回発見日と新着フラグの付与
    history_mgr = HistoryManager()
    events = history_mgr.update_events_with_history(events)
    recent_count = sum(1 for e in events if e.is_new)
    print(f"[HISTORY] 履歴と照合完了: 新着・最近追加イベント {recent_count} 件")

    # キャッシュの保存 (更新後の属性を含む)
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump([e.to_dict() for e in events], f, ensure_ascii=False, indent=2)
    print(f"[SAVE] キャッシュを保存しました: {CACHE_FILE}")

    print(f"\n[BUILD] Webページ & Markdownを生成中 (出力先: {args.output_dir})...")
    generator = PageGenerator(templates_dir="templates", output_dir=args.output_dir)
    generator.generate(events)

    html_file = os.path.abspath(os.path.join(args.output_dir, "index.html"))

    if args.open:
        print(f"[OPEN] ブラウザで開いています: {html_file}")
        webbrowser.open(f"file:///{html_file}")

    print("\n[COMPLETE] 全ての処理が正常に完了しました！")

if __name__ == "__main__":
    main()
