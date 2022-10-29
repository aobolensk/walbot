import base64
import os
import random
import re
import shutil
import tempfile
from typing import List

from src import const
from src.algorithms import levenshtein_distance
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.config import bc
from src.utils import Util


class _ImageInternals:
    @staticmethod
    async def get_image(execution_ctx, command):
        for i in range(1, len(command)):
            for root, _, files in os.walk(const.IMAGES_DIRECTORY):
                if not root.endswith(const.IMAGES_DIRECTORY):
                    continue
                for file in files:
                    if (not execution_ctx.silent and
                            os.path.splitext(os.path.basename(file))[0].lower() == command[i].lower()):
                        await Command.send_message(
                            execution_ctx, None, files=[os.path.join(const.IMAGES_DIRECTORY, file)])
                        break
                else:
                    # Custom emoji
                    r = const.DISCORD_EMOJI_REGEX.match(command[i])
                    if r is not None:
                        await Command.send_message(
                            execution_ctx, f"https://cdn.discordapp.com/emojis/{r.group(2)}.png")
                        break
                    # Unicode emoji
                    if const.UNICODE_EMOJI_REGEX.match(command[i]):
                        rq = Util.request("https://unicode.org/emoji/charts/full-emoji-list.html")
                        emojis_page = rq.get_text()
                        emoji_match = r"<img alt='{}' class='imga' src='data:image/png;base64,([^']+)'>"
                        emoji_match = re.findall(emoji_match.format(command[i]), emojis_page)
                        if emoji_match:
                            os.makedirs(Util.tmp_dir(), exist_ok=True)
                            with tempfile.NamedTemporaryFile(dir=Util.tmp_dir()) as temp_image_file:
                                with open(temp_image_file.name, 'wb') as f:
                                    f.write(base64.b64decode(emoji_match[4]))  # Twemoji is located under this index
                                shutil.copy(temp_image_file.name, temp_image_file.name + ".png")
                                await Command.send_message(
                                    execution_ctx, None, files=[temp_image_file.name + ".png"])
                                os.unlink(temp_image_file.name + ".png")
                            break
                    min_dist = 100000
                    suggestion = ""
                    for file in (os.path.splitext(os.path.basename(file))[0].lower() for file in files):
                        dist = levenshtein_distance(command[i], file)
                        if dist < min_dist:
                            suggestion = file
                            min_dist = dist
                    await Command.send_message(
                        execution_ctx, f"Image '{command[i]}' is not found! Probably you meant '{suggestion}'")
                break


class ImageCommands(BaseCmd):
    def __init__(self) -> None:
        pass

    def bind(self) -> None:
        bc.executor.commands["img"] = Command(
            "image", "img", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._img, max_execution_time=-1)
        bc.executor.commands["listimg"] = Command(
            "image", "listimg", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._listimg)

    async def _img(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Send image (use !listimg for list of available images)
    Example: !img <image_name>"""
        if not await Command.check_args_count(execution_ctx, cmd_line):
            return
        if len(cmd_line) > 1 + const.MAX_IMAGES_AMOUNT_FOR_IMG_COMMAND:
            return await Command.send_message(
                execution_ctx,
                "ERROR: Too many images were provided "
                f"({len(cmd_line) - 1} > {const.MAX_IMAGES_AMOUNT_FOR_IMG_COMMAND})")
        if len(cmd_line) == 1:
            try:
                list_images = os.listdir(const.IMAGES_DIRECTORY)
            except FileNotFoundError:
                return await Command.send_message(execution_ctx, "Images directory does not exist")
            if len(list_images) == 0:
                return await Command.send_message(execution_ctx, "No images found!")
            result = random.randint(0, len(list_images) - 1)  # integer random
            return await Command.send_message(
                execution_ctx, None,
                files=[os.path.join(const.IMAGES_DIRECTORY, list_images[result])])
        await _ImageInternals.get_image(execution_ctx, cmd_line)

    async def _listimg(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Print list of available images for !img command
    Example: !listimg"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        result = []
        for root, _, files in os.walk(const.IMAGES_DIRECTORY):
            if not root.endswith(const.IMAGES_DIRECTORY):
                continue
            for file in files:
                result.append(os.path.splitext(os.path.basename(file))[0])
        result.sort()
        if result:
            await Command.send_message(execution_ctx, "List of available images: [" + ', '.join(result) + "]")
        else:
            await Command.send_message(execution_ctx, "No available images found!")
