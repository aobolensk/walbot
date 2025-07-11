[![Lint](https://github.com/aobolensk/walbot/actions/workflows/lint.yml/badge.svg)](https://github.com/aobolensk/walbot/actions/workflows/lint.yml)
[![Test](https://github.com/aobolensk/walbot/actions/workflows/test.yml/badge.svg)](https://github.com/aobolensk/walbot/actions/workflows/test.yml)
[![Nightly](https://github.com/aobolensk/walbot/actions/workflows/nightly.yml/badge.svg)](https://github.com/aobolensk/walbot/actions/workflows/nightly.yml)
[![CodeQL](https://github.com/aobolensk/walbot/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/aobolensk/walbot/actions/workflows/codeql-analysis.yml)

[![codecov](https://codecov.io/gh/aobolensk/walbot/graph/badge.svg?token=1M1ZGOGSP9)](https://codecov.io/gh/aobolensk/walbot)

# walbot
Discord bot written in Python*

\* Bot has partial support for Telegram backend. See [supported backends](#supported-backends) section

### Supported backends

* Discord: [Setup guide](docs/SetupBackends.md#discord)
* Telegram: [Setup guide](docs/SetupBackends.md#telegram)

### Requirements:

#### Operating systems:
- Linux
- macOS
- Windows

#### Dependencies
##### Required

- libmagic<br>
  Windows:
  ```sh
  $ pip install python-magic-bin
  ```
  Debian/Ubuntu:
  ```sh
  $ sudo apt-get install libmagic-dev
  ```
  macOS:
  ```sh
  $ brew install libmagic
  ```
- [Python](https://www.python.org/) 3.9-3.13

##### Optional
- [ffmpeg](https://www.ffmpeg.org/) - for built-in DiscordVideoQueue plugin

### Quick start:
```shell
$ python -m pip install -r requirements.txt
$ python -m pip install -r requirements-extra.txt  # optional
$ python walbot.py start
```

or using [Poetry](https://python-poetry.org/)

```shell
$ poetry install
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

Patch tool docs: [Read](docs/Patch.md)<br>
Plugins tutorial: [Read](docs/PluginsTutorial.md)<br>
Feature flags: [Read](docs/FeatureFlags.md)<br>
FAQ: [Read](docs/FAQ.rst)<br>

#### Commands

Discord commands help: [Read](docs/DiscordCommands.md)<br>
Telegram commands help: [Read](docs/TelegramCommands.md)<br>
