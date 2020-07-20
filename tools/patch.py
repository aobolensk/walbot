import argparse
import os
import shutil
import sys

import yaml

try:
    sys.path.append(os.getcwd())
    from src.log import log
    from src.patch.updater import Updater
except ModuleNotFoundError as e:
    raise e


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


def save_file(path, config):
    try:
        yaml_dumper = yaml.CDumper
    except Exception:
        yaml_dumper = yaml.Dumper
    with open(path, 'wb') as f:
        f.write(yaml.dump(config, Dumper=yaml_dumper, encoding='utf-8', allow_unicode=True))


def main():
    parser = argparse.ArgumentParser(description='WalBot config patcher', formatter_class=argparse.RawTextHelpFormatter)
    files = [
        "config.yaml",
        "markov.yaml",
        "secret.yaml",
    ]
    parser.add_argument("file",
                        choices=[
                            "all",
                            *files,
                        ],
                        nargs='?',
                        default="all",
                        help='Config file to patch')
    args = parser.parse_args()
    if args.file != "all":
        files = [args.file]
    for file in files:
        config = read_file(file)
        if not hasattr(config, "version"):
            log.error("{} does not have 'version' field".format(file))
            sys.exit(1)
        version = config.version
        log.info("WalBot config patch tool: {}@{}".format(file, version))
        if Updater(file, config).result():
            if not os.path.exists("backup"):
                os.makedirs("backup")
            shutil.copyfile(file, "backup/" + file + ".bak." + version)
            save_file(file, config)
            log.info("Successfully saved file: {}".format(config.version))


if __name__ == "__main__":
    main()
