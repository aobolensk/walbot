import discord
import os
import yaml


class Config:
    def add_attributes(self):
        if not hasattr(self, "guilds"):
            self.guilds = {}
        if not hasattr(self, "token"):
            self.token = None

    def __init__(self):
        self.add_attributes()


class WalBot(discord.Client):
    def __init__(self, config):
        super(WalBot, self).__init__()
        self.config = config

    async def on_ready(self):
        print("Logged in as: {} {}".format(self.user.name, self.user.id))
        for guild in self.guilds:
            if guild.id not in self.config.guilds:
                self.config.guilds[guild.id] = dict()
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    self.config.guilds[guild.id][channel.id] = None

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.content.startswith("!ping"):
            await message.channel.send("Pong! " + message.author.mention)

def main():
    config = None
    if os.path.isfile("config.yaml"):
        with open("config.yaml", 'r') as f:
            config = yaml.load(f.read())
        config.add_attributes()
    if config is None:
        config = Config()
    walBot = WalBot(config)
    if config.token is None:
        config.token = input("Enter your token: ")
    walBot.run(config.token)
    print("Disconnected")
    print(config.guilds)
    with open('config.yaml', 'wb') as f:
        f.write(bytes(yaml.dump(config), encoding='utf8'))

if __name__ == "__main__":
    main()
