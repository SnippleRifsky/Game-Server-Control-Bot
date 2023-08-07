import discord
from apikeys import *
from ssh import init_ssh
from discord.ext import commands
from discord.utils import get

intents = discord.Intents.all()
discord.Intents.members = True
discord.Intents.guilds = True
client = commands.Bot(command_prefix='!', intents=intents)

BOTTOKEN = get_api_keys()

shell = init_ssh()


@client.event
async def on_ready():
    print("Starting the bot")
    print("------------------------------")
    # Automatically retrieve the guild ID
    guild = client.guilds[0] if client.guilds else None
    if guild:
        print(f"Connected to guild: {guild.name} (ID: {guild.id})")
        if get(guild.roles, name="Server Op"):
            print("Server Op role already exists")
        else:
            await discord.Guild.create_role(guild, name='Server Op')
            print("Creating Server Op role")
    else:
        print("Bot is not a member of any guilds.")
    print("Bot Initialized")
    print("------------------------------")

@client.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member):
    role = get(ctx.guild.roles, name="Server Op")
    await member.add_roles(role)
    await ctx.send("Given "+member.mention+" the "+role.name+" role.")


@client.command()
@commands.has_role('Server Op')
async def status(ctx):
    await ctx.send("Returning server status!")
    status = str(shell.sudo("systemctl status squad.service | grep Active"))
    for line in status.split('\n'):
        if 'Active' in line:
            await ctx.send("```python\n"+line+"```")


@client.command()
@commands.has_role('Server Op')
async def start(ctx):
    await ctx.send("Starting the server!")
    status = str(shell.sudo("systemctl start squad.service"))
    for line in status.split('\n'):
        if 'with status 0' in line:
            await ctx.send("```python\n"+"Server has started successfully!"+"```")


@client.command()
@commands.has_role('Server Op')
async def restart(ctx):
    await ctx.send("Restarting the server!")
    status = str(shell.sudo("systemctl restart squad.service"))
    for line in status.split('\n'):
        if 'with status 0' in line:
            await ctx.send("```python\n"+"Server has restarted successfully!"+"```")


@client.command()
@commands.has_role('Server Op')
async def stop(ctx):
    await ctx.send("Stopping the server!")
    status = str(shell.sudo("systemctl stop squad.service"))
    for line in status.split('\n'):
        if 'with status 0' in line:
            await ctx.send("```python\n"+"Server has stopped successfully!"+"```")


@client.command()
@commands.has_role('Server Op')
async def update(ctx):
    await ctx.send("Updating the server!\nThis may take a few minutes!")
    status = str(shell.run("./update.sh"))
    for line in status.split('\n'):
        if 'App ' in line:
            await ctx.send("```python\n"+line+"```")


@status.error
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingRole):
        role = get(ctx.guild.roles, name="Server Op")
        await ctx.send('Only the '+role.name+' role may use this command!')


@start.error
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingRole):
        role = get(ctx.guild.roles, name="Server Op")
        await ctx.send('Only the '+role.name+' role may use this command!')


@restart.error
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingRole):
        role = get(ctx.guild.roles, name="Server Op")
        await ctx.send('Only the '+role.name+' role may use this command!')


@stop.error
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingRole):
        role = get(ctx.guild.roles, name="Server Op")
        await ctx.send('Only the '+role.name+' role may use this command!')


@update.error
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingRole):
        role = get(ctx.guild.roles, name="Server Op")
        await ctx.send('Only the '+role.name+' role may use this command!')


@addrole.error
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingPermissions):
        await ctx.send('You do not have permissions to use this command')

client.run(BOTTOKEN)
