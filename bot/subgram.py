import json
import random
from pathlib import Path

import aiohttp

from . import config

SPONSORS_JSON = Path(__file__).resolve().parent.parent / "demo_sponsors.json"


class Sponsor:
    def __init__(self, sponsor_id: str, title: str, link: str, icon: str = "📢"):
        self.id = sponsor_id
        self.title = title
        self.link = link
        self.icon = icon

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "link": self.link, "icon": self.icon}


def _load_demo_sponsors() -> list[Sponsor]:
    if SPONSORS_JSON.exists():
        data = json.loads(SPONSORS_JSON.read_text(encoding="utf-8"))
        return [
            Sponsor(s["id"], s["title"], s["link"], s.get("icon", "📢"))
            for s in data
        ]
    return [
        Sponsor("demo1", "Demo Channel 1", "https://t.me/demo1"),
        Sponsor("demo2", "Demo Channel 2", "https://t.me/demo2"),
        Sponsor("demo3", "Demo Channel 3", "https://t.me/demo3"),
    ]


# ---------- real SubGram adapter ----------

async def _post(api_key: str, action: str, payload: dict) -> dict | None:
    url = f"{config.SUBGRAM_API_URL}/get-sponsors" if action == "get-sponsors" else f"{config.SUBGRAM_API_URL}/get-user-subscriptions"
    headers = {"Auth": api_key, "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return None
                return await resp.json()
        except (aiohttp.ClientError, TimeoutError):
            return None


async def get_sponsors_subgram(token: str, user_id: int, chat_id: int) -> list[dict]:
    data = await _post(
        token,
        "get-sponsors",
        {
            "chat_id": chat_id,
            "user_id": user_id,
            "action": "get_sponsors",
            "get_links": 1,
        },
    )
    if not data:
        return []
    sponsors = data.get("sponsors") or data.get("data") or []
    out = []
    for s in sponsors:
        if isinstance(s, dict):
            out.append(
                {
                    "id": str(s.get("id", s.get("channel_id", ""))),
                    "title": s.get("title", s.get("name", "Sponsor")),
                    "link": s.get("link", s.get("url", "")),
                    "icon": "📢",
                }
            )
    return out


async def user_subscribed_subgram(token: str, user_id: int, sponsor_ids: list[str]) -> bool:
    data = await _post(
        token,
        "get-user-subscriptions",
        {"user_id": user_id, "channel_ids": sponsor_ids},
    )
    if not data:
        return False
    subs = data.get("subscriptions") or data.get("data") or {}
    if isinstance(subs, dict):
        return all(subs.get(s) is True for s in sponsor_ids if s)
    return bool(subs)


# ---------- demo adapter ----------

async def get_sponsors_demo(user_id: int, chat_id: int) -> list[dict]:
    sponsors = _load_demo_sponsors()
    return [s.to_dict() for s in sponsors]


async def spend_cooldown_task(user_id: int) -> None:
    return None


# ---------- unified facade ----------

def demo_mode() -> bool:
    return config.DEMO_MODE or not config.SUBGRAM_BOT_API_KEY


async def get_sponsors(user_id: int, chat_id: int) -> list[dict]:
    if demo_mode():
        return await get_sponsors_demo(user_id, chat_id)
    return await get_sponsors_subgram(config.SUBGRAM_BOT_API_KEY, user_id, chat_id)


async def user_subscribed(user_id: int, sponsor_ids: list[str]) -> bool:
    if demo_mode():
        return True
    return await user_subscribed_subgram(config.SUBGRAM_BOT_API_KEY, user_id, sponsor_ids)