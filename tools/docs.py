import argparse
import os
import sys

try:
    sys.path.append(os.getcwd())
    from src import const
    from src.log import log
    from src.utils import Util
except ModuleNotFoundError as e:
    raise e


def main():
    parser = argparse.ArgumentParser(description='WalBot docs updater', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-o", "--out_file", default=const.COMMANDS_DOC_PATH,
                        help="Path to output file")
    args = parser.parse_args()
    log.info("Reading config.yaml")
    config = Util.read_config_file(const.CONFIG_PATH)
    config.commands.update()
    log.info("Exporting help to {}".format(args.out_file))
    config.commands.export_help(args.out_file)


if __name__ == "__main__":
    main()
