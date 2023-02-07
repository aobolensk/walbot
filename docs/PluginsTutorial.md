# Plugins Tutorial

### How to add new plugin

Create .py file in `src/plugins` directory using the following template

```py
from src.api.execution_context import ExecutionContext
from src.plugin import BasePlugin


class TestPlugin(BasePlugin):
    def __init__(self) -> None:
        super().__init__()

    async def init(self) -> None:
        await super().init()

    async def on_message(self, execution_ctx: ExecutionContext) -> None:
        await super().on_message(execution_ctx)
        if execution_ctx.platform == "discord":
            print(execution_ctx.message)
        elif execution_ctx.platform == "telegram":
            print(execution_ctx.update)
        else:
            pass

    async def close(self) -> None:
        await super().close()
```

Note: if you want to create private plugin module you need to create in in `src/plugins/private`. Private plugins are fully functional but they are separated from public ones and automatically gitignored.

## Plugin examples

### Custom command plugin example

```py
from src import const
from src.api.command import Command
from src.api.execution_context import ExecutionContext
from src.config import bc
from src.plugin import BasePlugin


class TestCommandPlugin(BasePlugin):
    def __init__(self) -> None:
        super().__init__()

    async def init(self) -> None:
        await super().init()
        await bc.plugin_manager.register_bot_command(self.get_classname(), "test", const.Permission.USER, self._test)

    async def _test(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Test command
    Example: !test"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1):
            return
        await Command.send_message(execution_ctx, "Hello from plugin!")


    async def on_message(self, execution_ctx: ExecutionContext) -> None:
        await super().on_message(execution_ctx)

    async def close(self) -> None:
        await super().close()
        await bc.plugin_manager.unregister_bot_command(self.get_classname(), "test")
```


### Background routine plugin example

```py
import asyncio

from src.api.execution_context import ExecutionContext
from src.log import log
from src.plugin import BasePlugin


class BackgroundRoutinePlugin(BasePlugin):
    def __init__(self) -> None:
        super().__init__()

    async def init(self) -> None:
        await super().init()
        self._task = bc.discord.background_loop.create_task(self._routine())

    async def _routine(self) -> None:
        while True:
            log.info("Hello from plugin!")
            await asyncio.sleep(3600)

    async def on_message(self, execution_ctx: ExecutionContext) -> None:
        await super().on_message(execution_ctx)

    async def close(self) -> None:
        await super().close()
        self._task.cancel()
```
