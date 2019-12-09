[![CI Status](https://github.com/gooddoog/walbot/workflows/Lint/badge.svg)](https://github.com/gooddoog/walbot/actions)

# walbot
Discord bot in Python

Requirements:
- Python 3.5+

Run:
```shell
$ python -m pip install -r requirements.txt
$ python main.py start
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
