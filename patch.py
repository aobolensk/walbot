import argparse
import os
import sys

import yaml

from src.log import log
from src.patch.updater import Updater


def read_file(path):
    try:
        yaml_loader = yaml.CLoader
    except Exception:
        yaml_loader = yaml.Loader
    if os.path.isfile(path):
        with open(path, 'r') as f:
            try:
                content = yaml.load(f.read(), Loader=yaml_loader)
            except Exception:
                log.error("File '{}' can not be read!".format(path))
    else:
        log.error("File '{}' does not exist!".format(path))
    return content


def main():
    parser = argparse.ArgumentParser(description='WalBot config patcher', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("file",
                        choices=[
                            "config.yaml",
                            "markov.yaml",
                            "secret.yaml"
                        ],
                        help='Config file to patch')
    args = parser.parse_args()
    config = read_file(args.file)
    if not hasattr(config, "version"):
        log.error("Config does not have 'version' field")
        sys.exit(1)
    log.info("WalBot config patch tool: {}@{}".format(args.file, config.version))
    Updater(args.file, config)


if __name__ == "__main__":
    main()
