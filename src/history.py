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

    def update_events_with_history(self, events: List[Event], recent_days: int = 7) -> List[Event]:
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
                # 新規発見されたイベント
                ev.first_seen_at = today_str
                newly_added_ids.add(ev.id)
                self.history[ev.id] = {
                    "first_seen_at": ev.first_seen_at,
                    "title": ev.title,
                    "venue": ev.venue
                }

            # 新着（is_new）判定:
            # 1. cutoff_date（直近7日）以内に追加された
            # 2. 今回新しく追加された
            # 3. 公式サイト側で「NEW」バッジがある
            if (ev.first_seen_at >= cutoff_date) or (ev.id in newly_added_ids) or ("NEW" in ev.status):
                ev.is_new = True
            else:
                ev.is_new = False

        self.save_history()
        return events

    @staticmethod
    def get_recent_events(events: List[Event], limit: int = 12) -> List[Event]:
        """最近追加された順（first_seen_at 降順）にソートして上位を返す"""
        # first_seen_at 降順を最優先でソート
        sorted_events = sorted(
            events,
            key=lambda e: (
                e.first_seen_at or "1970-01-01",
                1 if e.is_new else 0,
                1 if "NEW" in e.status else 0,
                1 if "開催中" in e.status else 0
            ),
            reverse=True
        )
        return sorted_events[:limit]
