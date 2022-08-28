from src import const
from src.api.command import SupportedPlatforms
from src.config import Config, bc
from src.log import log
from src.utils import Util


def main(args):
    log.info("Reading config.yaml")
    config = Util.read_config_file(const.CONFIG_PATH)
    if config is None:
        config = Config()
    config.commands.update()
    bc.executor.load_commands()
    log.info(f"Exporting help to {const.DISCORD_COMMANDS_DOC_PATH}")
    config.commands.export_help(const.DISCORD_COMMANDS_DOC_PATH)  # Discord legacy help export
    log.info(f"Exporting help to docs/{SupportedPlatforms.TELEGRAM.name.title()}Commands.md")
    bc.executor.export_help(SupportedPlatforms.TELEGRAM)
