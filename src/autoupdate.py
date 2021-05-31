import importlib
import time

from src import const


def start(args) -> None:
    au = importlib.import_module("src.autoupdate_impl")
    context = au.AutoUpdateContext()
    au.at_start()
    try:
        while True:
            time.sleep(const.AUTOUPDATE_CHECK_INTERVAL)
            is_updated = au.check_updates(context)
            if is_updated:
                au = importlib.reload(au)
    except KeyboardInterrupt as e:
        au.at_failure(e)
    au.at_exit()
