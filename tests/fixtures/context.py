from src import const
from src.api.execution_context import ExecutionContext


class BufferTestExecutionContext(ExecutionContext):
    def __init__(self) -> None:
        super().__init__()
        self.platform = const.BotBackend.DUMMY_BACKEND

    async def send_message(self, message: str, *args, **kwargs) -> None:
        if self.silent:
            return
        print(message)

    async def reply(self, message: str, *args, **kwargs) -> None:
        return await self.send_message(message, *args, **kwargs)

    async def send_direct_message(self, user_id: int, message: str, *args, **kwargs) -> None:
        return await self.send_message(message, *args, **kwargs)

    def disable_pings(self, message: str) -> str:
        return message

    def message_author(self) -> str:
        return ""

    def message_author_id(self) -> int:
        return 0

    def channel_name(self) -> str:
        return "console"

    def channel_id(self) -> int:
        return 0

    def bot_user_id(self) -> int:
        return 0
