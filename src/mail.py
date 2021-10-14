import functools
import smtplib
import traceback
from typing import Any, List

from src.config import SecretConfig, bc
from src.log import log


class Mail:
    def __init__(self, secret_config: SecretConfig) -> None:
        self.secrets = None
        if not all(secret_config.mail.values()):
            log.error("Email service cannot be initialized. Fill all mail fields in secret.yaml")
            return
        self.secrets = secret_config.mail

    def connect(self) -> None:
        self._server = smtplib.SMTP_SSL(self.secrets["smtp_server"])
        self._server.ehlo(self.secrets["email"])
        self._server.login(self.secrets["email"], self.secrets["password"])
        self._server.auth_plain()

    def disconnect(self) -> None:
        self._server.quit()

    def send(self, addrs: List[str], subject: str, message: str) -> None:
        if not self.secrets:
            return
        try:
            self.connect()
            all_addrs = addrs.copy()
            all_addrs.append(self.secrets["email"])
            result = (
                f"From: WalBot <{self.secrets['email']}>\n"
                f"To: {', '.join(addrs)}\n"
                f"Subject: {subject}\n"
                "\n" +
                message
            )
            self._server.sendmail(
                from_addr=self.secrets["email"],
                to_addrs=all_addrs,
                msg=result.encode("utf-8")
            )
            log.info(f"Sent message:\n'''\n{result}'''")
            self.disconnect()
        except Exception as e:
            log.error(f"Send e-mail failed: {e}", exc_info=True)

    @staticmethod
    def send_exception_info_to_admin_emails_async(func) -> Any:
        """Catches all exceptions and sends e-mail to admins if it happened.
        It should be used as a decorator"""
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                try:
                    bot_info = bc.info.get_full_info(2)
                except Exception:
                    log.warning("Failed to get bot info to attach to e-mail", exc_info=True)
                    bot_info = "ERROR: Failed to retrieve details, please refer to log file"
                if bc.secret_config.admin_email_list:
                    mail = Mail(bc.secret_config)
                    mail.send(
                        bc.secret_config.admin_email_list,
                        f"WalBot {func.__name__} failed",
                        f"{func.__name__} failed:\n"
                        f"{e}\n"
                        "\n"
                        f"Backtrace:\n"
                        f"{traceback.format_exc()}\n"
                        f"Details:\n"
                        f"{bot_info}"
                    )
                log.error(f"{func.__name__} failed", exc_info=True)
        return wrapped
