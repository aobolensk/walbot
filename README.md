[![CI Status](https://github.com/aobolensk/walbot/workflows/Lint/badge.svg)](https://github.com/aobolensk/walbot/actions)
[![CI Status](https://github.com/aobolensk/walbot/workflows/Test/badge.svg)](https://github.com/aobolensk/walbot/actions)

# walbot
Discord bot in Python*

\* It also has Telegram backend which is under development.

### Requirements:
- [ffmpeg](https://www.ffmpeg.org/)
- [Python](https://www.python.org/) 3.8-3.10

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
Commands tutorial: [Read](docs/CommandsTutorial.md)

#### Commands

Discord commands help: [Read](docs/DiscordCommands.md)
