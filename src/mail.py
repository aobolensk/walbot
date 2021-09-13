import smtplib
from typing import List

from src.config import SecretConfig
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
                f"To: {', '.join(all_addrs)}\n"
                f"Subject: {subject}\n"
                "\n" +
                message
            )
            self._server.sendmail(
                from_addr=self.secrets["email"],
                to_addrs=addrs,
                msg=result.encode("utf-8")
            )
            log.info(f"Sent message:\n'''\n{result}'''")
            self.disconnect()
        except Exception as e:
            log.error(f"Send e-mail failed: {e}", exc_info=True)
