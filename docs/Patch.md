# Patch tool

Patch tool is used for upgrading YAML configuration files. It parses YAML file and you can access config fields the same way you access them inside the bot.

The main point, is to sync configuration file fields with current changes in repository. For example, to prevent accessing fields that may not exist in old configs. So old configs can't be used with new version and vise versa.

### Creating new patches

To create new patch for one of YAML configs you need to do the following things:
1. Write transition patch in [updater.py](../src/patch/updater.py), you can take a look at examples there
1. Increase version of config in this patch
1. Bump corresponding version in [const.py](../src/const.py)

### Command line options:
```shell
$ python tools/patch.py               # Patch all .yaml files
$ python tools/patch.py config.yaml   # Patch config
$ python tools/patch.py markov.yaml   # Patch Markov model config
$ python tools/patch.py secret.yaml   # Patch secret config
$ python tools/patch.py -h            # Get help for patch tool

$ python main.py start --patch  # Start the bot and patch all config files
```
