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

    async def process_repetitions(execution_ctx: ExecutionContext) -> None:
        m = tuple(bc.message_cache.get(execution_ctx.channel_id(), i) for i in range(3))
        if (all(m) and m[0].message and m[0].message == m[1].message == m[2].message and
            (m[0].author != execution_ctx.bot_user_id() and
             m[1].author != execution_ctx.bot_user_id() and
             m[2].author != execution_ctx.bot_user_id())):
            await execution_ctx.send_message(m[0].message)
