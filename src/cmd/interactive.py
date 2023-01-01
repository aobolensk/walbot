import asyncio
from typing import List

from src import const, emoji
from src.api.command import (BaseCmd, Command, Implementation,
                             SupportedPlatforms)
from src.api.execution_context import ExecutionContext
from src.bc import DoNotUpdateFlag
from src.config import bc
from src.log import log
from src.utils import Util


class _InteractiveCmdsInternals:
    @staticmethod
    async def discord_poll(execution_ctx: ExecutionContext, duration: int, options: List[str]):
        poll_message = f"Poll is started! You have {duration} seconds to vote!\n"
        for i, option in enumerate(options):
            poll_message += emoji.alphabet[i] + " -> " + option + '\n'
        poll_message = await execution_ctx.send_message(poll_message)
        bc.do_not_update[DoNotUpdateFlag.POLL] += 1
        for i in range(len(options)):
            try:
                await poll_message.add_reaction(emoji.alphabet[i])
            except Exception:
                log.debug(f"Error on add_reaction: {emoji.alphabet[i]}")
        timestamps = [60]
        timestamps = [x for x in timestamps if x < duration]
        timestamps.append(duration)
        timestamps = (
            [timestamps[0]] + [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))])
        timestamps.reverse()
        remaining = duration
        for timestamp in timestamps:
            await asyncio.sleep(timestamp)
            remaining -= timestamp
            if remaining > 0:
                await Command.send_message(execution_ctx, f"Poll is still going! {remaining} seconds left")
            else:
                poll_message = poll_message.id
                poll_message = await execution_ctx.message.channel.fetch_message(poll_message)
                results = []
                possible_answers = emoji.alphabet[:len(options)]
                for index, reaction in enumerate(poll_message.reactions):
                    if str(reaction) in possible_answers:
                        results.append((reaction, options[index], reaction.count - 1))
                results.sort(key=lambda option: option[2], reverse=True)
                result_message = "Time is up! Results:\n"
                for result in results:
                    result_message += str(result[0]) + " -> " + result[1] + " -> votes: " + str(result[2]) + '\n'
                await Command.send_message(execution_ctx, result_message)
                for i in range(len(options)):
                    try:
                        await poll_message.remove_reaction(emoji.alphabet[i], poll_message.author)
                    except Exception:
                        log.debug(f"Error on remove_reaction: {emoji.alphabet[i]}")
                bc.do_not_update[DoNotUpdateFlag.POLL] -= 1
                return

    @staticmethod
    async def telegram_poll(execution_ctx: ExecutionContext, duration: int, options: List[str]):
        if duration == 0:
            duration = None
        execution_ctx.update.message.bot.send_poll(
            execution_ctx.update.effective_chat.id,
            "Poll", options,
            open_period=duration,
        )


class InteractiveCommands(BaseCmd):
    def __init__(self) -> None:
        pass

    def bind(self) -> None:
        bc.executor.commands["poll"] = Command(
            "interactive", "poll", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._poll,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))

    async def _poll(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Create poll and collect result after selected time
    Example: !poll 60 option 1;option 2;option 3"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3):
            return
        if execution_ctx.silent:
            return
        # Validate duration
        duration = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be duration in seconds")
        if duration is None:
            return
        max_duration = 24 * 60 * 60  # 1 day
        if execution_ctx.platform == const.BotBackend.TELEGRAM:
            max_duration = 600
        if duration > max_duration:
            return await Command.send_message(
                execution_ctx, f"Poll duration is too long (got: {duration}, max: {max_duration})")
        # Validate poll options
        options = ' '.join(cmd_line[2:])
        options = options.split(';')
        max_poll_options = 0
        if execution_ctx.platform == const.BotBackend.DISCORD:
            max_poll_options = 20
        elif execution_ctx.platform == const.BotBackend.TELEGRAM:
            max_poll_options = 10
        if len(options) > max_poll_options:
            return await Command.send_message(
                execution_ctx, f"Too many options for poll (got: {len(options)}, max: {max_poll_options})")
        # Run poll
        if execution_ctx.platform == const.BotBackend.DISCORD:
            await _InteractiveCmdsInternals.discord_poll(execution_ctx, duration, options)
        elif execution_ctx.platform == const.BotBackend.TELEGRAM:
            await _InteractiveCmdsInternals.telegram_poll(execution_ctx, duration, options)
        else:
            raise NotImplementedError
