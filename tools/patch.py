import os
import shutil
import sys

import yaml

from src.const import ExitStatus
from src.log import log
from src.patch.updater import Updater
from src.utils import Util


def save_file(path, config):
    _, yaml_dumper = Util.get_yaml()
    with open(path, 'wb') as f:
        f.write(yaml.dump(config, Dumper=yaml_dumper, encoding='utf-8', allow_unicode=True))


def main(args, files):
    if args.file != "all":
        files = [args.file]
    for file in files:
        config = Util.read_config_file(file)
        if config is None:
            log.error(f"File '{file}' does not exist")
            sys.exit(ExitStatus.CONFIG_FILE_ERROR)
        if not hasattr(config, "version"):
            log.error(f"{file} does not have 'version' field")
            sys.exit(ExitStatus.CONFIG_FILE_ERROR)
        version = config.version
        log.info(f"WalBot config patch tool: {file}@{version}")
        if Updater(file, config).result():
            if not os.path.exists("backup"):
                os.makedirs("backup")
            shutil.copyfile(file, "backup/" + file + "." + version + ".bak")
            save_file(file, config)
            log.info(f"Successfully saved file: {config.version}")
