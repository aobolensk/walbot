from src import const
from src.utils import Util


class Repl:
    markov = None
    quit = False

    def start(self) -> int:
        print("Reading markov.yaml...")
        self.markov = Util.read_config_file(const.MARKOV_PATH)
        print("markov.yaml is loaded")
        while not self.quit:
            try:
                command = input("> ")
                self._process(command.split())
            except (EOFError, KeyboardInterrupt):
                self._quit(None)
        return 0

    def _process(self, cmd: str) -> None:
        if len(cmd) == 0:
            pass
        elif cmd[0] in ("?", "help"):
            self._help(cmd)
        elif cmd[0] == "next":
            self._next(cmd)
        elif cmd[0] == "words":
            self._words(cmd)
        elif cmd[0] in ("q", "quit"):
            self._quit(cmd)
        else:
            print(f"Unknown command {cmd[0]}")

    def _help(self, _) -> None:
        print("- help : print this message")
        print("- next <word> : print list of next words")
        print("- words : list of words in Markov model")
        print("- quit : quit this REPL")

    def _next(self, cmd):
        if len(cmd) < 2:
            print(f"Too few arguments for command '{cmd[0]}'")
            return
        word = cmd[1]
        if word not in self.markov.model.keys():
            print(f"No such word '{word}' in Markov model")
            return
        print(self.markov.model[word].next)

    def _words(self, cmd):
        print(self.markov.model.keys())

    def _quit(self, _):
        self.quit = True
        print("Bye!")


def print_header():
    print("Markov explorer tool")
    print("Type 'help' to get list of commands")


def main(args):
    print_header()
    repl = Repl()
    return repl.start()
