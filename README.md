[![CI Status](https://github.com/aobolensk/walbot/workflows/Lint/badge.svg)](https://github.com/aobolensk/walbot/actions)

# walbot
Discord bot in Python

Requirements:
- Python 3.5+

Quick start:
```shell
$ python -m pip install -r requirements.txt
$ python main.py start
```

Command line options overview:
```shell
$ python main.py start          # Start the bot
$ python main.py stop           # Stop the bot
$ python main.py restart        # Restart the bot
$ python main.py suspend        # Start dummy bot (useful for maintenance)
$ python main.py -h             # Get help
```

### Documentation

Patch tool docs: [Read](docs/Patch.md) \
Builtin commands list: [Read](docs/Commands.md)

### How to setup fast YAML loader and dumper?

Debian/Ubuntu:
```console
$ sudo apt install python3-yaml
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
