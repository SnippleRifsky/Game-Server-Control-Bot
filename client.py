import discord
from discord.ext import commands


def init_client():

    intents = discord.Intents.all()
    discord.Intents.members = True
    discord.Intents.guilds = True
    client = commands.Bot(command_prefix='!', intents=intents)

    return client
