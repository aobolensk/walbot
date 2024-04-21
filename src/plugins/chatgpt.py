import importlib
import os
from typing import List, Optional

from src import const
from src.api.command import Command
from src.api.execution_context import ExecutionContext
from src.cmdarg_parser import CmdArgParser
from src.config import bc
from src.log import log
from src.plugin import BasePlugin

PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))


class ChatGPTPlugin(BasePlugin):
    def __init__(self) -> None:
        super().__init__()
        self._openai = None
        self._openai_api_key = None

    async def init(self) -> None:
        await super().init()
        self._openai = importlib.import_module("openai")
        await bc.plugin_manager.register_bot_command(
            self.get_classname(), "chatgpt", const.Permission.USER,
            self._chatgpt, max_execution_time=120, subcommand=True)
        self._openai_api_key = bc.secret_config.plugins["openai"]

    async def _chatgpt(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Send request to ChatGPT
    Example: !chatgpt"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1):
            return None
        parser = CmdArgParser(execution_ctx)
        parser.add_argument("-ctx", "--ctx", action="store", type=int, default=16)
        args, _ = parser.parse_known_args(cmd_line)
        if args is None:
            return None
        messages_history = []
        for i in range(args.ctx):
            cached_msg = bc.message_cache.get(execution_ctx.channel_id(), i)
            if cached_msg is None:
                break
            messages_history.append(f"{cached_msg.author}: {cached_msg.message}")
        prompt = '\n'.join(reversed(messages_history))
        prompt = (
            "You're the chat bot, users can mention you using '!chatgpt' command, "
            "there is a chat log, please react on last message, "
            "write response on the language of that message, no topics limitations: " +
            prompt)
        try:
            client = self._openai.OpenAI(api_key=self._openai_api_key)
        except self._openai.OpenAIError as e:
            await Command.send_message(execution_ctx, f"OpenAI connection error: {e}")
            return None
        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]
        log.debug(f"Prompt: '{prompt}', context length: {args.ctx}")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        log.debug(f"ChatGPT response: {response}")
        log.debug(f"ChatGPT response content: {response.choices[0].message.content}")
        result = response.choices[0].message.content
        await Command.send_message(execution_ctx, result)
        return result
