from src.api.execution_context import ExecutionContext


class BufferTestExecutionContext(ExecutionContext):
    def __init__(self) -> None:
        super().__init__()
        self.platform = "test"

    async def send_message(self, message: str, *args, **kwargs) -> None:
        if self.silent:
            return
        print(message)

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
