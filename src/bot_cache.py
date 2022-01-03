from src.db.walbot_db import WalbotDatabase


class BotCache:
    def get_state(self) -> dict:
        self._state = self._db.find_one({"type": self._bot_type})
        return self._state

    def __init__(self, main_bot: bool) -> None:
        self._db = WalbotDatabase().bot_cache
        self._bot_type = "main_bot" if main_bot else "mini_bot"

    def update(self, upd_dict: dict) -> None:
        self.get_state()
        for key, value in upd_dict.items():
            self._state[key] = value
        self._db.update_one(
            {"type": self._bot_type},
            {"$set": self._state}
        )
        self._state = self._db.find_one({"type": self._bot_type})

    def parse(self) -> dict:
        return self.get_state()

    def dump_to_file(self) -> None:
        pass

    def remove(self) -> bool:
        self.update({
            "ready": False,
            "pid": None,
            "do_not_update": False,
        })
        return True

    def exists(self) -> bool:
        return True
