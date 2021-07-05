import datetime
from typing import Optional

import discord

from src import const


class DiscordEmbed:
    """Discord embed constructor"""

    def __init__(self) -> None:
        self._data = dict()

    def get(self) -> discord.Embed:
        """Get embed result"""
        return discord.Embed.from_dict(self._data)

    def title(self, title: str) -> None:
        """Add title"""
        self._data["title"] = title

    def title_url(self, title_url: str) -> None:
        """Specify title url"""
        self._data["url"] = title_url

    def description(self, description: str) -> None:
        """Add description"""
        self._data["description"] = description

    def color(self, color: int) -> None:
        """Specify left side strip color"""
        self._data["color"] = color

    def timestamp(self, datetime: datetime.datetime) -> None:
        self._data["timestamp"] = datetime.strftime(const.EMBED_TIMESTAMP_FORMAT)

    def add_field(self, title: str, text: str, inline: bool = False) -> None:
        """Add field"""
        if "fields" not in self._data.keys():
            self._data["fields"] = list()
        self._data["fields"].append({
            "name": title,
            "value": text,
            "inline": inline,
        })

    def footer(self, text: Optional[str] = None, icon_url: Optional[str] = None) -> None:
        """Add footer"""
        self._data["footer"] = dict()
        if text is not None:
            self._data["footer"]["text"] = text
        if icon_url is not None:
            self._data["footer"]["icon_url"] = icon_url

    def thumbnail(self, thumbnail_url: str) -> None:
        """Add thumbnail using image url"""
        self._data["thumbnail"] = dict()
        self._data["thumbnail"]["url"] = thumbnail_url

    def image(self, image_url: str) -> None:
        """Add image using image url"""
        self._data["image"] = dict()
        self._data["image"]["url"] = image_url

    def author(self, name: Optional[str] = None, url: Optional[str] = None, icon_url: Optional[str] = None) -> None:
        """Specify embed author"""
        self._data["author"] = dict()
        if name is not None:
            self._data["author"]["name"] = name
        if url is not None:
            self._data["author"]["url"] = url
        if icon_url is not None:
            self._data["author"]["icon_url"] = icon_url
