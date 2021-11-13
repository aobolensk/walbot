[![CI Status](https://github.com/aobolensk/walbot/workflows/Lint/badge.svg)](https://github.com/aobolensk/walbot/actions)
[![CI Status](https://github.com/aobolensk/walbot/workflows/Test/badge.svg)](https://github.com/aobolensk/walbot/actions)

# walbot
Discord bot in Python

### Requirements:
- [ffmpeg](https://www.ffmpeg.org/)
- [Python](https://www.python.org/) 3.7-3.10*

\* `numba` package is unavailable on Python 3.10, note that some functionality may be slower.

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
$ python walbot.py docs           # Generate commands documentation

# Start the bot and enable automatic update (requires starting from git repo)
$ python walbot.py autoupdate
$ python walbot.py start --autoupdate

# Run tests and tools
$ python walbot.py test           # Run walbot tests
$ python walbot.py patch          # Patch config files
$ python walbot.py mexplorer      # Run Markov model explorer

$ python walbot.py help           # Get help
```

### Documentation

Patch tool docs: [Read](docs/Patch.md) \
Builtin commands list: [Read](docs/Commands.md) \
Commands tutorial: [Read](docs/CommandsTutorial.md)

### How to setup fast YAML loader and dumper?

```console
$ sudo apt install python3-yaml    # Debian/Ubuntu
$ sudo pacman -S python-yaml       # Arch Linux/Manjaro
```
Alternative:
```console
$ git clone https://github.com/yaml/pyyaml
$ cd pyyaml
$ sudo python setup.py --with-libyaml install
```

### Setting up bot autorestart on system startup

Requirements:
- cron
- tmux

Setup example:
- Run `crontab -e`
- Add the following line to the file:
  ```sh
  @reboot /bin/sleep 5 && /usr/bin/tmux new-session -ds walbot 'cd <path-to-walbot> && <path-to-python3> walbot.py autoupdate --name "your-bot-instance-name"'
  ```

### Using walbot in Docker container

```console
$ docker build -t walbot .
$ docker run -it walbot /bin/bash
```
