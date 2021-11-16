# Plugins Tutorial

### How to add new plugin

1. Create .py file in `src/plugins` directory using the following template

```py
import asyncio

import discord

from src.log import log
from src.plugin import BasePlugin


class DummyPlugin(BasePlugin):
    def __init__(self) -> None:
        super().__init__()

    async def init(self) -> None:
        await super().init()
        try:
            loop = asyncio.get_running_loop()
            self._task = loop.create_task(self._routine())
        except Exception:
            log.error("", exc_info=True)

    async def _routine(self) -> None:
        while True:
            log.info("Hello, world!")
            await asyncio.sleep(3600)

    async def on_message(self, message: discord.Message) -> None:
        await super().on_message(message)
        log.info(f"Message: {message}")

    async def close(self) -> None:
        await super().close()

```

Note: if you want to create private plugin module you need to create in in `src/plugins/private`. Private plugins are fully functional but they are separated from public ones and automatically gitignored.
