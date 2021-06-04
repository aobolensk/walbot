from dataclasses import dataclass

import discord


@dataclass
class VoiceQueueEntry:
    channel: discord.TextChannel
    title: str
    id: str
    file_name: str
    requested_by: str
