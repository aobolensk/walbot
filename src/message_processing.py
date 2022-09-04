import re

from src import const
from src.api.command import Command
from src.api.execution_context import ExecutionContext
from src.config import bc


class MessageProcessing:
    async def process_responses(execution_ctx: ExecutionContext, message: str) -> None:
        responses_count = 0
        for response in bc.config.responses.values():
            if responses_count >= const.MAX_BOT_RESPONSES_ON_ONE_MESSAGE:
                break
            if re.search(response.regex, message):
                result = await Command.process_subcommands(execution_ctx, bc.executor, response.text)
                await execution_ctx.reply(result)
                responses_count += 1
