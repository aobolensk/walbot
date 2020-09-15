import os
import subprocess

import yaml

from . import const
from .log import log


class Util:
    @staticmethod
    async def response(message, content, silent, **kwargs):
        if not silent:
            msg = None
            if content:
                for chunk in Util.split_by_chunks(content, const.DISCORD_MAX_MESSAGE_LENGTH):
                    msg = await message.channel.send(
                        chunk,
                        tts=kwargs.get("tts", False),
                        files=kwargs.get("files", None))
                    if kwargs.get("suppress_embeds", False):
                        await msg.edit(suppress=True)
            elif kwargs.get("files", None):
                msg = await message.channel.send(None, files=kwargs.get("files", None))
            if kwargs.get("embed", None):
                msg = await message.channel.send(embed=kwargs["embed"], tts=kwargs.get("tts", False))
                if kwargs.get("suppress_embeds", False):
                    await msg.edit(suppress=True)
            return msg
        else:
            log.info("[SILENT] -> " + content)

    @staticmethod
    async def send_direct_message(author, content, silent, **kwargs):
        if not silent:
            if author.dm_channel is None:
                await author.create_dm()
            if content:
                for chunk in Util.split_by_chunks(content, const.DISCORD_MAX_MESSAGE_LENGTH):
                    msg = await author.dm_channel.send(
                        chunk,
                        tts=kwargs.get("tts", False),
                        files=kwargs.get("files", None))
                    if kwargs.get("suppress_embeds", False):
                        await msg.edit(suppress=True)
            elif kwargs.get("files", None):
                msg = await author.dm_channel.send(None, files=kwargs.get("files", None))
        else:
            log.info("[SILENT] -> " + content)

    @staticmethod
    async def check_args_count(message, command, silent, min=None, max=None):
        if min and len(command) < min:
            await Util.response(message, f"Too few arguments for command '{command[0]}'", silent)
            return False
        if max and len(command) > max:
            await Util.response(message, f"Too many arguments for command '{command[0]}'", silent)
            return False
        return True

    @staticmethod
    def split_by_chunks(message, count):
        for i in range(0, len(message), count):
            yield message[i:i+count]

    @staticmethod
    async def parse_int(message, string, error_message, silent):
        try:
            return int(string)
        except ValueError:
            await Util.response(message, error_message, silent)
            return

    @staticmethod
    async def parse_float(message, string, error_message, silent):
        try:
            return float(string)
        except ValueError:
            await Util.response(message, error_message, silent)
            return

    @staticmethod
    def check_version(name, actual, expected):
        if (actual != expected):
            log.error(f"{name} versions mismatch. Expected: {expected}, but actual: {actual}")
            return False
        return True

    @staticmethod
    async def run_external_command(message, cmd_line, silent=False):
        result = ""
        try:
            log.debug(f"Processing external command: '{cmd_line}'")
            process = subprocess.run(cmd_line, shell=True, check=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log.debug(f"External command '{cmd_line}' finished execution with return code: {process.returncode}")
            result = process.stdout.decode("utf-8")
            await Util.response(message, result, silent)
        except subprocess.CalledProcessError as e:
            await Util.response(message, f"<Command failed with error code {e.returncode}>", silent)
        return result

    @staticmethod
    def read_config_file(path):
        yaml_loader = Util.YAML.get_loader()
        if os.path.isfile(path):
            with open(path, 'r') as f:
                try:
                    return yaml.load(f.read(), Loader=yaml_loader)
                except Exception:
                    log.error(f"File '{path}' can not be read!", exc_info=True)
        return None

    class YAML:
        @staticmethod
        def get_loader(verbose=False):
            try:
                loader = yaml.CLoader
                if verbose:
                    log.debug("Using fast YAML Loader")
            except AttributeError:
                loader = yaml.Loader
                if verbose:
                    log.debug("Using slow YAML Loader")
            return loader

        @staticmethod
        def get_dumper(verbose=False):
            try:
                dumper = yaml.CDumper
                if verbose:
                    log.debug("Using fast YAML Dumper")
            except AttributeError:
                dumper = yaml.Dumper
                if verbose:
                    log.debug("Using slow YAML Dumper")
            return dumper
