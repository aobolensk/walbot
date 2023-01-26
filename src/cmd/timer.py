"""Timer and stopwatch"""

import asyncio
import datetime
from typing import List

from src import const
from src.api.command import (BaseCmd, Command, Implementation,
                             SupportedPlatforms)
from src.api.execution_context import ExecutionContext
from src.backend.discord.message import Msg
from src.bc import DoNotUpdateFlag
from src.config import bc
from src.utils import Time, Util


class TimerCommands(BaseCmd):
    def bind(self):
        bc.executor.commands["timer"] = Command(
            "timer", "timer", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._timer, max_execution_time=-1,
            supported_platforms=SupportedPlatforms.DISCORD)
        bc.executor.commands["stoptimer"] = Command(
            "timer", "stoptimer", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._stoptimer,
            supported_platforms=SupportedPlatforms.DISCORD)
        bc.executor.commands["stopwatch"] = Command(
            "timer", "stopwatch", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._stopwatch, max_execution_time=-1,
            supported_platforms=SupportedPlatforms.DISCORD)
        bc.executor.commands["stopstopwatch"] = Command(
            "timer", "stopstopwatch", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._stopstopwatch,
            supported_platforms=SupportedPlatforms.DISCORD)

    async def _timer(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Set timer
    Usage: !timer 10"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        start = Time().now()
        duration = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be duration in seconds")
        if duration is None:
            return
        if duration < 0:
            return await Command.send_message(execution_ctx, "Timer duration should be more than 0 seconds")
        if duration > const.MAX_TIMER_DURATION_IN_SECONDS:
            return await Command.send_message(execution_ctx, "Timer duration should be less than 24 hours")
        finish = Time().now() + datetime.timedelta(seconds=duration)
        id_ = bc.config.ids["timer"]
        bc.config.ids["timer"] += 1
        timer_msg = await Msg.response(execution_ctx.message, f"⏰ Timer #{id_}: {finish - start}", execution_ctx.silent)
        bc.do_not_update[DoNotUpdateFlag.TIMER] += 1
        bc.timers[id_] = True
        print_counter = 0
        while True:
            current = Time().now()
            if not bc.timers[id_]:
                await timer_msg.edit(content=f"⏰ Timer #{id_}: {finish - current}! (stopped)")
                bc.do_not_update[DoNotUpdateFlag.TIMER] -= 1
                break
            if current >= finish:
                await timer_msg.edit(content=f"⏰ Timer #{id_}: 0:00:00.000000!")
                await Command.send_message(execution_ctx, f"⏰ Timer #{id_}: Time is up!")
                bc.do_not_update[DoNotUpdateFlag.TIMER] -= 1
                break
            print_counter += 1
            if print_counter >= 10 * bc.do_not_update[DoNotUpdateFlag.TIMER]:
                await timer_msg.edit(content=f"⏰ Timer #{id_}: {finish - current}")
                print_counter = 0
            await asyncio.sleep(0.1)

    async def _stoptimer(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Stop timer
    Usage: !stoptimer 1"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        id_ = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an integer")
        if id_ is None:
            return
        if id_ not in bc.timers.keys():
            return await Command.send_message(execution_ctx, f"⏰ Unknown timer id: {id_}")
        bc.timers[id_] = False
        await Command.send_message(execution_ctx, f"⏰ Timer #{id_} is stopped!")

    async def _stopwatch(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Start stopwatch
    Usage: !stopwatch"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        start = Time().now()
        id_ = bc.config.ids["stopwatch"]
        bc.config.ids["stopwatch"] += 1
        stopwatch_msg = await Msg.response(
            execution_ctx.message, f"⏰ Stopwatch #{id_}: {start - start}", execution_ctx.silent)
        bc.do_not_update[DoNotUpdateFlag.STOPWATCH] += 1
        bc.stopwatches[id_] = True
        print_counter = 0
        while True:
            current = Time().now()
            if not bc.stopwatches[id_]:
                await stopwatch_msg.edit(content=f"⏰ Stopwatch #{id_}: {current - start}! (stopped)")
                bc.do_not_update[DoNotUpdateFlag.STOPWATCH] -= 1
                break
            print_counter += 1
            if print_counter >= 10 * bc.do_not_update[DoNotUpdateFlag.STOPWATCH]:
                await stopwatch_msg.edit(content=f"⏰ Stopwatch #{id_}: {current - start}")
                print_counter = 0
            await asyncio.sleep(0.1)

    async def _stopstopwatch(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Stop stopwatch
    Usage: !stopstopwatch 1"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        id_ = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an integer")
        if id_ is None:
            return
        if id_ not in bc.stopwatches.keys():
            return await Command.send_message(execution_ctx, f"⏰ Unknown stopwatch id: {id_}")
        bc.stopwatches[id_] = False
        await Command.send_message(execution_ctx, f"⏰ Stopwatch #{id_} is stopped!")
