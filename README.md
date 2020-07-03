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

### How to setup fast YAML loader and dumper?

Debian/Ubuntu:
```console
$ sudo apt install libyaml-dev
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

### Patch tool command line options:
```shell
$ python patch.py               # Patch all .yaml files
$ python patch.py config.yaml   # Patch config
$ python patch.py markov.yaml   # Patch Markov model config
$ python patch.py secret.yaml   # Patch Secret model config
$ python patch.py -h            # Get help for patch tool

$ python main.py start --patch  # Start the bot and patch all config files
```
