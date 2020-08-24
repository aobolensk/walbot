[![CI Status](https://github.com/aobolensk/walbot/workflows/Lint/badge.svg)](https://github.com/aobolensk/walbot/actions)

# walbot
Discord bot in Python

### Requirements:
- Python 3.6+

### Quick start:
```shell
$ python -m pip install -r requirements.txt
$ python walbot.py start
```

### Command line options overview:
```shell
$ python walbot.py start          # Start the bot
$ python walbot.py stop           # Stop the bot
$ python walbot.py restart        # Restart the bot
$ python walbot.py suspend        # Start dummy bot (useful for maintenance)
$ python walbot.py -h             # Get help
```

### Documentation

Patch tool docs: [Read](docs/Patch.md) \
Builtin commands list: [Read](docs/Commands.md) \
Commands tutorial: [Read](docs/CommandsTutorial.md)

### How to setup fast YAML loader and dumper?

Debian/Ubuntu:
```console
$ sudo apt install python3-yaml
```
Arch Linux/Manjaro:
```console
$ sudo pacman -S python-yaml
```
Alternative:
```console
$ git clone https://github.com/yaml/pyyaml
$ cd pyyaml
$ sudo python setup.py --with-libyaml install
```

### Using walbot in Docker container

```console
$ docker build -t walbot .
$ docker run -it walbot /bin/bash
```
