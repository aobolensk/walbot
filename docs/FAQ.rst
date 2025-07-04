FAQ
===

.. contents::

See also `Feature flags <FeatureFlags.md>`_ for optional environment variables.

How to setup fast YAML loader and dumper?
-----------------------------------------

.. code-block:: bash

  $ sudo apt install python3-yaml    # Debian/Ubuntu
  $ sudo pacman -S python-yaml       # Arch Linux/Manjaro

Alternative:

.. code-block:: bash

  $ git clone https://github.com/yaml/pyyaml
  $ cd pyyaml
  $ sudo python setup.py --with-libyaml install

Setting up bot autorestart on system startup
--------------------------------------------

Requirements:

- cron
- tmux

Setup example:

- Run `crontab -e`
- Add the following line to the file:

.. code-block:: bash

  @reboot /bin/sleep 5 && /usr/bin/tmux new-session -ds walbot 'cd <path-to-walbot> && <path-to-python3> walbot.py autoupdate --name "your-bot-instance-name"'

Using walbot in Docker container
--------------------------------

.. code-block:: bash

  $ docker build -f docker/default.Dockerfile -t walbot .
  $ docker run -it walbot /bin/bash
