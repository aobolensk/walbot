from src.patch.updater import Updater


def main(args, files):
    if args.file != "all":
        files = [args.file]
    for file in files:
        file = file.split('.')[0]  # Drop .yaml suffix
        updater = Updater(file)
        updater.update()
