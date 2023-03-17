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
    bc.executor.load_commands()
    config.commands.update()
    log.info(f"Exporting help to {const.DISCORD_COMMANDS_DOC_PATH}")
    log.info(f"Exporting help to docs/{SupportedPlatforms.TELEGRAM.name.title()}Commands.md")
    bc.executor.export_help(SupportedPlatforms.DISCORD)
    bc.executor.export_help(SupportedPlatforms.TELEGRAM)
