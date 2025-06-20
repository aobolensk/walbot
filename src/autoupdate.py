import importlib
import signal
import time

from src import const
from src.ff import FF
from src.log import log


def start(args) -> const.ExitStatus:
    au = importlib.import_module("src.autoupdate_impl")
    signal.signal(signal.SIGHUP, au.at_exit)
    try:
        context = au.AutoUpdateContext()
    except RuntimeError as e:
        log.error(e)
        return const.ExitStatus.GENERAL_ERROR
    au.at_start()
    try:
        while True:
            time.sleep(
                const.AUTOUPDATE_CHECK_INTERVAL
                if not FF.is_enabled("WALBOT_TEST_AUTO_UPDATE")
                else const.AUTOUPDATE_CHECK_INTERVAL_TEST)
            is_updated = au.check_updates(context)
            if is_updated:
                importlib.reload(au)
                signal.signal(signal.SIGHUP, au.at_exit)
                log.debug("Reloaded autoupdate implementation module")
    except KeyboardInterrupt as e:
        au.at_exit(e)
    except Exception as e:
        au.at_failure(e)
        raise e
    return const.ExitStatus.NO_ERROR
