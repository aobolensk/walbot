"""Timer and stopwatch"""

import asyncio
import datetime

from src import const
from src.backend.discord.message import Msg
from src.bc import DoNotUpdateFlag
from src.commands import BaseCmd
from src.config import bc
from src.utils import Util, null


class TimerCommands(BaseCmd):
    def bind(self):
        bc.commands.register_commands(__name__, self.get_classname(), {
            "timer": dict(permission=const.Permission.USER.value, subcommand=False, max_execution_time=-1),
            "stoptimer": dict(permission=const.Permission.USER.value, subcommand=False),
            "stopwatch": dict(permission=const.Permission.USER.value, subcommand=False, max_execution_time=-1),
            "stopstopwatch": dict(permission=const.Permission.USER.value, subcommand=False),
        })

    @staticmethod
    async def _timer(message, command, silent=False):
        """Set timer
    Usage: !timer 10"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        start = datetime.datetime.now()
        duration = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be duration in seconds", silent)
        if duration is None:
            return
        if duration < 0:
            return null(await Msg.response(message, "Timer duration should be more than 0 seconds", silent))
        if duration > const.MAX_TIMER_DURATION_IN_SECONDS:
            return null(await Msg.response(message, "Timer duration should be less than 24 hours", silent))
        finish = datetime.datetime.now() + datetime.timedelta(seconds=duration)
        id_ = bc.config.ids["timer"]
        bc.config.ids["timer"] += 1
        timer_msg = await Msg.response(message, f"⏰ Timer #{id_}: {finish - start}", silent)
        bc.do_not_update[DoNotUpdateFlag.TIMER] += 1
        bc.timers[id_] = True
        print_counter = 0
        while True:
            current = datetime.datetime.now()
            if not bc.timers[id_]:
                await timer_msg.edit(content=f"⏰ Timer #{id_}: {finish - current}! (stopped)")
                bc.do_not_update[DoNotUpdateFlag.TIMER] -= 1
                break
            if current >= finish:
                await timer_msg.edit(content=f"⏰ Timer #{id_}: 0:00:00.000000!")
                await Msg.response(message, f"⏰ Timer #{id_}: Time is up!", silent)
                bc.do_not_update[DoNotUpdateFlag.TIMER] -= 1
                break
            print_counter += 1
            if print_counter >= 10 * bc.do_not_update[DoNotUpdateFlag.TIMER]:
                await timer_msg.edit(content=f"⏰ Timer #{id_}: {finish - current}")
                print_counter = 0
            await asyncio.sleep(0.1)

    @staticmethod
    async def _stoptimer(message, command, silent=False):
        """Stop timer
    Usage: !stoptimer 1"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        id_ = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an integer", silent)
        if id_ is None:
            return
        if id_ not in bc.timers.keys():
            return null(await Msg.response(message, f"⏰ Unknown timer id: {id_}", silent))
        bc.timers[id_] = False
        await Msg.response(message, f"⏰ Timer #{id_} is stopped!", silent)

    @staticmethod
    async def _stopwatch(message, command, silent=False):
        """Start stopwatch
    Usage: !stopwatch"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        start = datetime.datetime.now()
        id_ = bc.config.ids["stopwatch"]
        bc.config.ids["stopwatch"] += 1
        stopwatch_msg = await Msg.response(message, f"⏰ Stopwatch #{id_}: {start - start}", silent)
        bc.do_not_update[DoNotUpdateFlag.STOPWATCH] += 1
        bc.stopwatches[id_] = True
        print_counter = 0
        while True:
            current = datetime.datetime.now()
            if not bc.stopwatches[id_]:
                await stopwatch_msg.edit(content=f"⏰ Stopwatch #{id_}: {current - start}! (stopped)")
                bc.do_not_update[DoNotUpdateFlag.STOPWATCH] -= 1
                break
            print_counter += 1
            if print_counter >= 10 * bc.do_not_update[DoNotUpdateFlag.STOPWATCH]:
                await stopwatch_msg.edit(content=f"⏰ Stopwatch #{id_}: {current - start}")
                print_counter = 0
            await asyncio.sleep(0.1)

    @staticmethod
    async def _stopstopwatch(message, command, silent=False):
        """Stop stopwatch
    Usage: !stopstopwatch 1"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        id_ = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an integer", silent)
        if id_ is None:
            return
        if id_ not in bc.stopwatches.keys():
            return null(await Msg.response(message, f"⏰ Unknown stopwatch id: {id_}", silent))
        bc.stopwatches[id_] = False
        await Msg.response(message, f"⏰ Stopwatch #{id_} is stopped!", silent)
