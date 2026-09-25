import os
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict
from src.models import Event
import logging

logger = logging.getLogger(__name__)
JST = timezone(timedelta(hours=9))

class HistoryManager:
    """イベントの初回発見日時（first_seen_at）を永続化し、最近追加されたイベントを判定・追跡するクラス"""
    def __init__(self, history_file: str = "data/events_history.json"):
        self.history_file = os.path.abspath(history_file)
        self.history: Dict[str, dict] = self._load_history()

    def _load_history(self) -> Dict[str, dict]:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load history file: {e}")
        return {}

    def save_history(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved event history ({len(self.history)} records) to {self.history_file}")
        except Exception as e:
            logger.error(f"Failed to save history file: {e}")

    def update_events_with_history(self, events: List[Event], recent_days: int = 14) -> List[Event]:
        """イベント一覧に first_seen_at と is_new フラグを付与する"""
        today_dt = datetime.now(JST)
        today_str = today_dt.strftime("%Y-%m-%d")
        cutoff_date = (today_dt - timedelta(days=recent_days)).strftime("%Y-%m-%d")

        is_first_run = (len(self.history) == 0)
        newly_added_ids = set()

        for idx, ev in enumerate(events):
            if ev.id in self.history:
                # 既存の履歴から初回発見日を引き継ぐ
                record = self.history[ev.id]
                ev.first_seen_at = record.get("first_seen_at", today_str)
            else:
                # 初回登録（新規発見）
                if is_first_run:
                    # 初回実行時は、先頭の新しいイベント（またはNEW/注目が付いているもの）に段階的な日付を付与
                    if idx < 12 or "NEW" in ev.status or "注目" in ev.status or "予告" in ev.status:
                        ev.first_seen_at = today_str
                        newly_added_ids.add(ev.id)
                    else:
                        prev_days = 15 + (idx % 20)
                        ev.first_seen_at = (today_dt - timedelta(days=prev_days)).strftime("%Y-%m-%d")
                else:
                    ev.first_seen_at = today_str
                    newly_added_ids.add(ev.id)

                self.history[ev.id] = {
                    "first_seen_at": ev.first_seen_at,
                    "title": ev.title,
                    "venue": ev.venue
                }

            # 新着（is_new）判定:
            # 1. cutoff_date 以降に追加された
            # 2. 今回新しく追加された
            # 3. 公式サイト側で「NEW」や「注目」バッジがある
            if (ev.first_seen_at >= cutoff_date) or (ev.id in newly_added_ids) or ("NEW" in ev.status):
                ev.is_new = True
            else:
                ev.is_new = False

        self.save_history()
        return events

    @staticmethod
    def get_recent_events(events: List[Event], limit: int = 8) -> List[Event]:
        """最近追加された順にソートして上位を返す"""
        # is_new なイベントを優先し、first_seen_at 降順でソート
        sorted_events = sorted(
            events,
            key=lambda e: (
                1 if e.is_new else 0,
                1 if "NEW" in e.status else 0,
                e.first_seen_at or "1970-01-01",
                1 if "開催中" in e.status else 0
            ),
            reverse=True
        )
        return sorted_events[:limit]
