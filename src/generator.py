import os
import shutil
import json
from datetime import datetime, timezone, timedelta
from jinja2 import Environment, FileSystemLoader
from typing import List
from src.models import Event
import logging

logger = logging.getLogger(__name__)

# 日本時間 (JST)
JST = timezone(timedelta(hours=9))

class PageGenerator:
    def __init__(self, templates_dir: str = "templates", output_dir: str = "dist"):
        self.templates_dir = os.path.abspath(templates_dir)
        self.output_dir = os.path.abspath(output_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=True
        )

    def generate(self, events: List[Event]):
        os.makedirs(self.output_dir, exist_ok=True)
        now_str = datetime.now(JST).strftime("%Y年%m月%d日 %H:%M")
        
        # 統計の集計
        total_events = len(events)
        open_events = sum(1 for e in events if "開催中" in e.status or "上映中" in e.status)
        venues = set(e.venue for e in events if e.venue)
        
        stats = {
            "total_events": total_events,
            "open_events": open_events,
            "venues_count": len(venues)
        }
        
        # 1. HTMLの生成
        html_template = self.jinja_env.get_template("index.html.jinja")
        html_content = html_template.render(
            events=events,
            stats=stats,
            generated_at=now_str
        )
        html_path = os.path.join(self.output_dir, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"Generated HTML page: {html_path}")

        # 2. Markdownの生成
        md_template = self.jinja_env.get_template("events.md.jinja")
        md_content = md_template.render(
            events=events,
            stats=stats,
            generated_at=now_str
        )
        md_path = os.path.join(self.output_dir, "events.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        logger.info(f"Generated Markdown: {md_path}")

        # 3. JSONデータの書き出し
        json_path = os.path.join(self.output_dir, "events.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in events], f, ensure_ascii=False, indent=2)
        logger.info(f"Generated JSON: {json_path}")

        # 4. アセット（CSS, JS）のコピー
        src_assets = os.path.join(self.templates_dir, "assets")
        dst_assets = os.path.join(self.output_dir, "assets")
        if os.path.exists(src_assets):
            if os.path.exists(dst_assets):
                shutil.rmtree(dst_assets)
            shutil.copytree(src_assets, dst_assets)
            logger.info(f"Copied assets to: {dst_assets}")

        print(f"\n[OK] ページ生成が完了しました！")
        print(f" -> HTML: {html_path}")
        print(f" -> Markdown: {md_path}")
        print(f" -> JSON: {json_path}")
