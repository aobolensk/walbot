import discord

class WalBot(discord.Client):
    async def on_ready(self):
        print("Logged in as: {} {}".format(self.user.name, self.user.id))

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.content.startswith("!ping"):
            await message.channel.send("Pong! " + message.author.mention)

def main():
    walBot = WalBot()
    walBot.run(input("Enter your token: "))

if __name__ == "__main__":
    main()
