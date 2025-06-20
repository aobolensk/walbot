import base64
import os
import random
import re
import shutil
import tempfile
import urllib
from typing import List

import magic

from src import const
from src.algorithms import levenshtein_distance
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.config import bc
from src.log import log
from src.utils import Util


class _ImageInternals:
    @staticmethod
    async def get_image(execution_ctx: ExecutionContext, cmd_line: List[str]):
        for i in range(1, len(cmd_line)):
            for root, _, files in os.walk(const.IMAGES_DIRECTORY):
                if not root.endswith(const.IMAGES_DIRECTORY):
                    continue
                for file in files:
                    if (not execution_ctx.silent and
                            os.path.splitext(os.path.basename(file))[0].lower() == cmd_line[i].lower()):
                        await Command.send_message(
                            execution_ctx, None, files=[os.path.join(const.IMAGES_DIRECTORY, file)])
                        break
                else:
                    # Custom emoji
                    r = const.DISCORD_EMOJI_REGEX.match(cmd_line[i])
                    if r is not None:
                        await Command.send_message(
                            execution_ctx, f"https://cdn.discordapp.com/emojis/{r.group(2)}.png")
                        break
                    # Unicode emoji
                    if const.UNICODE_EMOJI_REGEX.match(cmd_line[i]):
                        rq = Util.request("https://unicode.org/emoji/charts/full-emoji-list.html")
                        emojis_page = rq.get_text()
                        emoji_match = r"<img alt='{}' class='imga' src='data:image/png;base64,([^']+)'>"
                        emoji_match = re.findall(emoji_match.format(cmd_line[i]), emojis_page)
                        if emoji_match:
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
                        dist = levenshtein_distance(cmd_line[i], file)
                        if dist < min_dist:
                            suggestion = file
                            min_dist = dist
                    await Command.send_message(
                        execution_ctx, f"Image '{cmd_line[i]}' is not found! Probably you meant '{suggestion}'")
                break

    @staticmethod
    async def add_image(execution_ctx: ExecutionContext, cmd_line: List[str], update: bool) -> None:
        name = cmd_line[1]
        if not re.match(const.FILENAME_REGEX, name):
            return await Command.send_message(execution_ctx, f"Incorrect name '{name}'")
        url = cmd_line[2]
        ext = urllib.parse.urlparse(url).path.split('.')[-1]
        if ext not in ["jpg", "jpeg", "png", "ico", "gif", "bmp"]:
            return await Command.send_message(execution_ctx, "Please, provide direct link to image")

        found = False
        for root, _, files in os.walk(const.IMAGES_DIRECTORY):
            if not root.endswith(const.IMAGES_DIRECTORY):
                continue
            for file in files:
                if name == os.path.splitext(os.path.basename(file))[0]:
                    found = True
                    if not update:
                        return await Command.send_message(execution_ctx, f"Image '{name}' already exists")
        if update and not found:
            return await Command.send_message(execution_ctx, f"Image '{name}' does not exist")

        image_path = os.path.join(const.IMAGES_DIRECTORY, name + '.' + ext)
        with open(image_path, 'wb') as f:
            try:
                hdr = {
                    "User-Agent": "Mozilla/5.0"
                }
                rq = urllib.request.Request(url, headers=hdr)
                with urllib.request.urlopen(rq) as response:
                    f.write(response.read())
            except ValueError:
                return await Command.send_message(execution_ctx, "Incorrect image URL format!")
            except Exception as e:
                os.remove(image_path)
                log.error("Image downloading failed!", exc_info=True)
                return await Command.send_message(execution_ctx, f"Image downloading failed: {e}")

        file_mime = magic.from_file(image_path, mime=True)
        if "image/" not in file_mime:
            log.debug(magic.from_file(image_path, mime=True))
            log.error(f"Received file is not an image: {file_mime}")
            os.remove(image_path)
            log.info(f"Removed file {image_path}")
            return await Command.send_message(execution_ctx, f"Received file is not an image. MIME: {file_mime}")

        if not update:
            await Command.send_message(execution_ctx, f"Image '{name}' is successfully added!")
        else:
            await Command.send_message(execution_ctx, f"Image '{name}' is successfully updated!")


class ImageCommands(BaseCmd):
    def bind(self) -> None:
        bc.executor.commands["img"] = Command(
            "image", "img", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._img, max_execution_time=-1)
        bc.executor.commands["addimg"] = Command(
            "image", "addimg", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._addimg)
        bc.executor.commands["updimg"] = Command(
            "image", "updimg", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._updimg)
        bc.executor.commands["listimg"] = Command(
            "image", "listimg", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._listimg)
        bc.executor.commands["delimg"] = Command(
            "image", "delimg", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._delimg)

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

    async def _addimg(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Add image for !img command
    Example: !addimg name url"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3, max=3):
            return
        await _ImageInternals.add_image(execution_ctx, cmd_line, update=False)

    async def _updimg(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Update image for !img command
    Example: !updimg name url"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3, max=3):
            return
        await _ImageInternals.add_image(execution_ctx, cmd_line, update=True)

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

    async def _delimg(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Delete image for !img command
    Example: !delimg name"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        name = cmd_line[1]
        if not re.match(const.FILENAME_REGEX, name):
            return await Command.send_message(execution_ctx, f"Incorrect name '{name}'")
        for root, _, files in os.walk(const.IMAGES_DIRECTORY):
            if not root.endswith(const.IMAGES_DIRECTORY):
                continue
            for file in files:
                if name == os.path.splitext(os.path.basename(file))[0]:
                    os.remove(os.path.join(const.IMAGES_DIRECTORY, file))
                    return await Command.send_message(execution_ctx, f"Successfully removed image '{name}'")
        await Command.send_message(execution_ctx, f"Image '{name}' not found!")
