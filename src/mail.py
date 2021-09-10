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

    def send(self, addrs: List[str], subject: str, message: str) -> None:
        if not self.secrets:
            return
        server = smtplib.SMTP_SSL(self.secrets["smtp_server"])
        server.ehlo(self.secrets["email"])
        server.login(self.secrets["email"], self.secrets["password"])
        server.auth_plain()
        all_addrs = addrs.copy()
        all_addrs.append(self.secrets["email"])
        result = (
            f"From: WalBot <{self.secrets['email']}>\n"
            f"To: {', '.join(addrs)}\n"
            f"Subject: {subject}\n"
            "\n" +
            message
        )
        server.sendmail(
            from_addr=self.secrets["email"],
            to_addrs=addrs,
            msg=result.encode("utf-8")
        )
        log.info(f"Sent message:\n'''\n{result}'''")
        server.quit()
