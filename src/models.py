from dataclasses import dataclass, asdict
from typing import Optional
import hashlib
import json

@dataclass
class Event:
    id: str
    title: str
    venue: str
    area: str
    period: str
    status: str
    genre: str
    description: str
    image_url: str
    link_url: str
    source: str
    updated_at: str
    first_seen_at: str = ""
    is_new: bool = False

    @classmethod
    def create(
        cls,
        title: str,
        venue: str,
        area: str,
        period: str = "",
        status: str = "上映中",
        genre: str = "プラネタリウム",
        description: str = "",
        image_url: str = "",
        link_url: str = "",
        source: str = "",
        updated_at: str = "",
        first_seen_at: str = "",
        is_new: bool = False
    ):
        raw_key = f"{title}_{venue}_{link_url}".encode('utf-8')
        event_id = hashlib.md5(raw_key).hexdigest()[:12]
        return cls(
            id=event_id,
            title=title.strip(),
            venue=venue.strip(),
            area=area.strip(),
            period=period.strip(),
            status=status.strip(),
            genre=genre.strip(),
            description=description.strip(),
            image_url=image_url.strip(),
            link_url=link_url.strip(),
            source=source.strip(),
            updated_at=updated_at.strip(),
            first_seen_at=first_seen_at.strip(),
            is_new=is_new
        )

    def to_dict(self):
        return asdict(self)
