import asyncio
import importlib
import logging

import pytest

from src.plugins.chatgpt import ChatGPTPlugin


@pytest.mark.asyncio
async def test_init_handles_missing_openai(monkeypatch, caplog):
    plugin = ChatGPTPlugin()

    def fake_import(name, package=None):
        if name == "openai":
            raise ImportError("No module named 'openai'")
        return importlib.import_module(name, package)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    caplog.set_level(logging.ERROR, logger="WalBot")

    await plugin.init()

    assert any("openai" in record.getMessage() for record in caplog.records)
    assert not await plugin.is_enabled()
