import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import logging
from typing import List
from src.models import Event

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
}

def clean_text(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.split())

class WalkerplusScraper:
    """ウォーカープラスのプラネタリウム検索結果をスクレイピング"""
    BASE_URL = "https://www.walkerplus.com"
    SEARCH_URL = "https://www.walkerplus.com/search/planetarium/"

    def __init__(self, max_pages: int = 4):
        self.max_pages = max_pages

    def scrape(self) -> List[Event]:
        events = []
        now_str = datetime.now().strftime("%Y-%m-%d")
        
        for page in range(1, self.max_pages + 1):
            if page == 1:
                url = self.SEARCH_URL
            else:
                url = f"{self.SEARCH_URL}{page}.html"
                
            logger.info(f"[Walkerplus] Fetching page {page}: {url}")
            try:
                res = requests.get(url, headers=DEFAULT_HEADERS, timeout=12)
                if res.status_code != 200:
                    logger.warning(f"[Walkerplus] Status {res.status_code} on page {page}. Stopping.")
                    break
                    
                soup = BeautifulSoup(res.content, "lxml")
                items = soup.select(".m-mainlist-item")
                if not items:
                    logger.info(f"[Walkerplus] No items found on page {page}. End of list.")
                    break
                    
                for item in items:
                    ttl_el = item.select_one(".m-mainlist-item__ttl")
                    if not ttl_el:
                        continue
                    title = clean_text(ttl_el.get_text())
                    
                    link_el = item.select_one("a[href*='/event/']")
                    href = link_el['href'] if link_el else ""
                    if href.startswith("/"):
                        full_link = f"{self.BASE_URL}{href}"
                    else:
                        full_link = href
                        
                    # Period and status
                    status = "開催中"
                    period_el = item.select_one(".m-mainlist-item-event__period")
                    period_text = ""
                    if period_el:
                        open_badge = period_el.select_one(".m-mainlist-item-event__open")
                        if open_badge:
                            status = clean_text(open_badge.get_text())
                        period_text = clean_text(period_el.get_text().replace(status, ""))
                    
                    # Description
                    desc_el = item.select_one(".m-mainlist-item__txt")
                    desc = clean_text(desc_el.get_text()) if desc_el else ""
                    
                    # Area & Venue
                    area = "全国"
                    map_links = item.select(".m-mainlist-item__maplink")
                    if map_links:
                        area = " ".join([clean_text(m.get_text()) for m in map_links])
                        
                    venue_el = item.select_one(".m-mainlist-item-event__placelink")
                    venue = clean_text(venue_el.get_text()) if venue_el else "各地のプラネタリウム"
                    
                    # Image
                    image_url = ""
                    img_el = item.select_one("img[src*='ms-cache'], img[data-src*='ms-cache']")
                    if img_el:
                        src = img_el.get("data-src") or img_el.get("src") or ""
                        if src.startswith("//"):
                            image_url = f"https:{src}"
                        elif src.startswith("http"):
                            image_url = src
                            
                    # Genre tag
                    genre = "プラネタリウム"
                    tag_el = item.select_one(".m-mainlist-item__tagsitemlink")
                    if tag_el:
                        genre = clean_text(tag_el.get_text())
                        
                    ev = Event.create(
                        title=title,
                        venue=venue,
                        area=area,
                        period=period_text,
                        status=status,
                        genre=genre,
                        description=desc,
                        image_url=image_url,
                        link_url=full_link,
                        source="ウォーカープラス",
                        updated_at=now_str
                    )
                    events.append(ev)
                    
                time.sleep(0.5) # Gentle crawling
            except Exception as e:
                logger.error(f"[Walkerplus] Error on page {page}: {e}")
                break
                
        logger.info(f"[Walkerplus] Collected {len(events)} events.")
        return events


class KonicaMinoltaScraper:
    """コニカミノルタプラネタリウム直営館の上映作品およびイベントをスクレイピング"""
    BASE_URL = "https://planetarium.konicaminolta.jp"

    def scrape(self) -> List[Event]:
        events = []
        now_str = datetime.now().strftime("%Y-%m-%d")
        
        # 1. 上映作品 (/programs/)
        logger.info("[KonicaMinolta] Scraping programs from /programs/...")
        try:
            url = f"{self.BASE_URL}/programs/"
            res = requests.get(url, headers=DEFAULT_HEADERS, timeout=12)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "lxml")
                cards = soup.select(".card-body, .post-wrapper")
                for card in cards:
                    title_el = card.select_one(".post_title .body__large, .p-program-title, h3")
                    if not title_el:
                        continue
                    title = clean_text(title_el.get_text())
                    if not title or title == "作品詳細":
                        continue
                        
                    link_el = card.select_one("a[href*='/program/']")
                    href = link_el['href'] if link_el else ""
                    if href.startswith("/"):
                        full_link = f"{self.BASE_URL}{href}"
                    else:
                        full_link = href
                        
                    img_el = card.select_one("img.card-img, img[src*='uploads']")
                    image_url = ""
                    if img_el:
                        src = img_el.get("src") or ""
                        if src.startswith("/"):
                            image_url = f"{self.BASE_URL}{src}"
                        elif src.startswith("http"):
                            image_url = src
                            
                    genre_el = card.select_one(".genre")
                    genre = clean_text(genre_el.get_text()) if genre_el else "プラネタリウム"
                    
                    status_badge = card.select_one(".badge")
                    status = clean_text(status_badge.get_text()) if status_badge else "上映中"
                    
                    concept_el = card.select_one(".concept, .post-text p")
                    desc = clean_text(concept_el.get_text()) if concept_el else ""
                    
                    # 開催館の判定
                    halls = []
                    text_all = card.get_text()
                    hall_names = {
                        "planetariatokyo": "プラネタリアTOKYO(有楽町)",
                        "manten": "満天(池袋)",
                        "tenku": "天空(押上)",
                        "planetariayokohama": "プラネタリアYOKOHAMA",
                        "manten-nagoya": "満天NAGOYA"
                    }
                    for input_tag in card.select("input[type='hidden']"):
                        val = input_tag.get("value", "")
                        if val in hall_names:
                            halls.append(hall_names[val])
                            
                    venue = " / ".join(halls) if halls else "コニカミノルタプラネタリウム各館"
                    area = "東京・神奈川・愛知" if halls else "全国主要都市"
                    
                    ev = Event.create(
                        title=title,
                        venue=venue,
                        area=area,
                        period="上映中（詳細は公式スケジュール参照）",
                        status=status,
                        genre=genre,
                        description=desc,
                        image_url=image_url,
                        link_url=full_link,
                        source="コニカミノルタ公式",
                        updated_at=now_str
                    )
                    events.append(ev)
        except Exception as e:
            logger.error(f"[KonicaMinolta] Error scraping programs: {e}")

        # 2. イベント・フェア (/event/)
        logger.info("[KonicaMinolta] Scraping events from /event/...")
        try:
            url = f"{self.BASE_URL}/event/"
            res = requests.get(url, headers=DEFAULT_HEADERS, timeout=12)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "lxml")
                # イベント記事リンク
                for a in soup.select("a[href*='/event/']"):
                    href = a.get("href", "")
                    if href.endswith("/event/") or href.endswith("/archive") or href.endswith("/recruit/"):
                        continue
                    title = clean_text(a.get_text())
                    if len(title) < 5 or "アルバイト" in title or "アンケート" in title:
                        continue
                        
                    full_link = f"{self.BASE_URL}{href}" if href.startswith("/") else href
                    
                    # 画像検索
                    parent = a.find_parent("li") or a.find_parent("article") or a.find_parent("div")
                    image_url = ""
                    desc = ""
                    if parent:
                        img = parent.find("img")
                        if img and img.get("src"):
                            src = img.get("src")
                            image_url = f"{self.BASE_URL}{src}" if src.startswith("/") else src
                        desc_el = parent.find("p")
                        if desc_el:
                            desc = clean_text(desc_el.get_text())
                            
                    # 会場推定
                    venue = "コニカミノルタプラネタリウム"
                    area = "首都圏・愛知"
                    if "プラネタリアTOKYO" in title or "有楽町" in title:
                        venue = "プラネタリアTOKYO（有楽町）"
                        area = "東京都"
                    elif "天空" in title:
                        venue = "プラネタリウム天空（押上）"
                        area = "東京都"
                    elif "満天" in title and "NAGOYA" not in title:
                        venue = "プラネタリウム満天（池袋）"
                        area = "東京都"
                    elif "YOKOHAMA" in title or "横浜" in title:
                        venue = "プラネタリアYOKOHAMA"
                        area = "神奈川県"
                    elif "NAGOYA" in title or "名古屋" in title:
                        venue = "プラネタリウム満天NAGOYA"
                        area = "愛知県"
                        
                    ev = Event.create(
                        title=title,
                        venue=venue,
                        area=area,
                        period="最新イベント・期間限定",
                        status="注目",
                        genre="特別イベント",
                        description=desc or f"{venue}で開催される注目の限定イベント・フェア情報です。",
                        image_url=image_url,
                        link_url=full_link,
                        source="コニカミノルタ公式",
                        updated_at=now_str
                    )
                    events.append(ev)
        except Exception as e:
            logger.error(f"[KonicaMinolta] Error scraping events: {e}")
            
        logger.info(f"[KonicaMinolta] Collected {len(events)} events.")
        return events


class MiraikanScraper:
    """日本科学未来館 ドームシアターの最新上映をスクレイピング"""
    BASE_URL = "https://www.miraikan.jst.go.jp"
    DOME_URL = "https://www.miraikan.jst.go.jp/exhibitions/dometheater/"

    def scrape(self) -> List[Event]:
        events = []
        now_str = datetime.now().strftime("%Y-%m-%d")
        logger.info("[Miraikan] Scraping dome theater programs...")
        
        try:
            res = requests.get(self.DOME_URL, headers=DEFAULT_HEADERS, timeout=12)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "lxml")
                # ドームシアター上映作品のリンク
                seen_links = set()
                for a in soup.select("a[href*='/exhibitions/dometheater/']"):
                    href = a.get("href", "")
                    if href in [self.DOME_URL, "/exhibitions/dometheater/", "/exhibitions/dometheater/movie-archive/"]:
                        continue
                    if href in seen_links:
                        continue
                        
                    title = clean_text(a.get_text())
                    if not title or len(title) < 3:
                        continue
                        
                    full_link = f"{self.BASE_URL}{href}" if href.startswith("/") else href
                    seen_links.add(href)
                    
                    # 画像や概要を探す
                    parent = a.find_parent("div") or a.find_parent("li") or a.find_parent("article")
                    image_url = ""
                    desc = ""
                    if parent:
                        img = parent.find("img")
                        if img and img.get("src"):
                            src = img.get("src")
                            image_url = f"{self.BASE_URL}{src}" if src.startswith("/") else src
                        # Extract description if available
                        for p in parent.find_all("p"):
                            ptxt = clean_text(p.get_text())
                            if ptxt and ptxt != title:
                                desc = ptxt
                                break
                                
                    ev = Event.create(
                        title=title,
                        venue="日本科学未来館 ドームシアターガイア",
                        area="東京都 江東区（お台場）",
                        period="常設・定期上映（要事前予約・スケジュール確認）",
                        status="上映中",
                        genre="科学・3Dドーム映像",
                        description=desc or "超高精細な立体視映像システムを備えたドームシアターで上映される科学・宇宙プログラム。",
                        image_url=image_url,
                        link_url=full_link,
                        source="日本科学未来館",
                        updated_at=now_str
                    )
                    events.append(ev)
        except Exception as e:
            logger.error(f"[Miraikan] Error scraping dometheater: {e}")
            
        logger.info(f"[Miraikan] Collected {len(events)} events.")
        return events


class PlanetariumAggregator:
    """複数のスクレイパーを統括し、イベントデータを集約・重複排除する"""
    def __init__(self):
        self.scrapers = [
            WalkerplusScraper(max_pages=4),
            KonicaMinoltaScraper(),
            MiraikanScraper()
        ]

    def aggregate(self) -> List[Event]:
        all_events: List[Event] = []
        for scraper in self.scrapers:
            try:
                events = scraper.scrape()
                all_events.extend(events)
            except Exception as e:
                logger.error(f"Error in {scraper.__class__.__name__}: {e}")
                
        # 重複排除 (タイトル類似度やURLで重複を除去)
        unique_events = []
        seen_keys = set()
        for ev in all_events:
            # 簡易正規化キー: タイトルから空白・記号等を除去
            norm_title = "".join(c for c in ev.title.lower() if c.isalnum() or c in "ぁ-んァ-ヶー一-龯")[:15]
            key = (norm_title, ev.venue[:8])
            if key in seen_keys:
                continue
            seen_keys.add(key)
            unique_events.append(ev)
            
        logger.info(f"Total aggregated unique events: {len(unique_events)}")
        return unique_events
