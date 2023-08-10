import discord
import time
import re
from fabric import exceptions as fabric_exceptions
from invoke import exceptions as invoke_exceptions
from apikeys import *
from ssh import init_ssh
from discord.ext import commands
from discord.utils import get

intents = discord.Intents.all()
discord.Intents.members = True
discord.Intents.guilds = True
client = commands.Bot(command_prefix="!", intents=intents)

BOTTOKEN = get_api_keys()


@client.event
async def on_ready():
    print("Starting the bot")
    print("------------------------------")

    # Automatically retrieve the guild ID
    guild = client.guilds[0] if client.guilds else None
    if guild:
        print(f"Connected to guild: {guild.name} (ID: {guild.id})")

        # Initialize the SSH shell
        shell = init_ssh()
        client.extra_events["shell"] = shell  # Attach to client.extra_events

        if get(guild.roles, name="Server Op"):
            print("Server Op role already exists")
        else:
            await discord.Guild.create_role(guild, name="Server Op")
            print("Creating Server Op role")
    else:
        print("Bot is not a member of any guilds.")

    print("Bot Initialized")
    print("------------------------------")


@client.command()
@commands.has_role("Server Op")
async def lpapply(ctx, *args):
    shell = ctx.bot.extra_events["shell"]
    
    # Join all arguments into a single string, enclosed in single quotes
    arg = " ".join(args)
    if not arg:
        await ctx.send("Please provide an argument.")
        return

    # Execute ./minecraft_command.sh with 'arg' enclosed in single quotes via SSH
    lpapply_command = f"./minecraft_command.sh '{arg}'"
    try:
        shell.run(lpapply_command, hide=True)
    except Exception as e:
        print(f"An error occurred while running the command: {e}")
        await ctx.send("An error occurred while running the command.")
        return
    
    # Check if the session expired warning is present
    session_expired_command = f"grep -A 2 '{arg}' logs/latest.log | grep 'The changes received from the web editor are based'"
    session_expired_output = shell.run(session_expired_command, hide=True)
    
    session_expired_line = session_expired_output.stdout.strip()
    
    # If the session expired warning is found, return the following 3 lines
    if session_expired_line:
        session_expired_lines = session_expired_line.split('\n')
        await ctx.send("```" + '\n'.join(session_expired_lines) + "```")
        return
    
    # Find the last occurrence of web editor data being applied in the logs
    last_apply_command = f"grep 'Web editor data was applied to' logs/latest.log* | tail -n 1"
    last_apply_output = shell.run(last_apply_command, hide=True)
    
    last_apply_line = last_apply_output.stdout.strip()
    
    # Extract the timestamp from the log
    timestamp_line = last_apply_line
    
    # If timestamp found, read the logs and filter for lines with the same timestamp
    lines_with_timestamp = []
    if timestamp_line:
        timestamp = timestamp_line.split("[")[1].split("]")[0]
        with shell.cd("logs"):
            logs_command = f"grep -h '{timestamp}' latest.log* | grep -v '{timestamp_line}'"
            logs_output = shell.run(logs_command, hide=True)
            for line in logs_output.stdout.strip().split("\n"):
                lines_with_timestamp.append(line)
    
    # Send the filtered lines to Discord
    await ctx.send("```python\n" + "\n".join(lines_with_timestamp) + "\n```")



@client.command()
@commands.has_role("Server Op")
async def lpedit(ctx):
    shell = ctx.bot.extra_events["shell"]

    # Execute ./minecraft_command.sh 'lp editor' via SSH
    lpedit_command = "./minecraft_command.sh 'lp editor'"
    try:
        shell.run(lpedit_command, hide=True)
    except Exception as e:
        print(f"An error occurred while running the command: {e}")
        pass

    # Introduce a 2-second delay
    time.sleep(1)

    # Find the last occurrence of new lp editor session in the logs
    last_lpedit_command = (
        "grep 'Preparing a new editor session' logs/latest.log* | tail -n 1"
    )
    last_lpedit_output = shell.run(last_lpedit_command, hide=True)

    last_lpedit_line = last_lpedit_output.stdout.strip()

    # Get the next line after the last_lpedit_line
    editor_link = shell.run("tail -n 1 logs/latest.log*", hide=True).stdout.strip()

    # Define a regular expression pattern for timestamp and header
    pattern = re.compile(r"\[\d{2}:\d{2}:\d{2}\] \[luckperms-command-executor/INFO\]: ")

    # Remove the timestamp and header pattern using regular expressions
    sanitized_last_lpedit_line = pattern.sub("", last_lpedit_line)
    sanitized_editor_link = pattern.sub("", editor_link)

    formatted_message = f"`{sanitized_last_lpedit_line}`\n{sanitized_editor_link}"

    await ctx.send(formatted_message)
    await ctx.send("If the session needs to be trusted, use `!lptrust`")


@client.command()
@commands.has_role("Server Op")
async def lptrust(ctx):
    shell = ctx.bot.extra_events["shell"]

    # Find the last occurrence of "If it was you, run" line in the logs
    lptrust_command = "grep 'If it was you, run' logs/latest.log* | tail -n 1"
    lptrust_output = shell.run(lptrust_command, hide=True).stdout.strip()

    # Extract the session_key from the line using regular expressions
    pattern = re.compile(r"run (.* )?to")
    match = pattern.search(lptrust_output)
    if match:
        session_key = match.group(1).strip()

        # Execute ./minecraft_command.sh 'session_key' via SSH
        trust_command = f"./minecraft_command.sh '{session_key}'"
        try:
            shell.run(trust_command, hide=True)
            await ctx.send(f"Successfully executed the command: {trust_command}")
        except Exception as e:
            print(f"An error occurred while running the command: {e}")
            await ctx.send(f"An error occurred while running the command: {e}")
    else:
        await ctx.send("No suitable session key found in the logs.")


@client.command()
@commands.has_role("Server Op")
async def list(ctx):
    shell = ctx.bot.extra_events["shell"]
    await ctx.send("Fetching player list...")

    # Execute ./minecraft_command.sh list via SSH
    list_command = "./minecraft_command.sh list"
    try:
        shell.run(list_command, hide=True)
    except Exception as e:
        print(f"An error occurred while running the command: {e}")
        pass

    # Find the last occurrence of "players online" in the logs
    last_players_online_command = "grep 'players online' logs/latest.log* | tail -n 1"
    last_players_online_output = shell.run(last_players_online_command, hide=True)

    last_players_online_line = last_players_online_output.stdout.strip()

    # Extract timestamp from the last "players online" line
    last_timestamp = last_players_online_line.split("[")[1].split("]")[0]

    # Search for lines with the same timestamp in the logs
    lines_with_timestamp_command = f"grep '\\[{last_timestamp}\\]' logs/latest.log* | grep -v 'CONSOLE issued server command: /list'"
    lines_with_timestamp_output = shell.run(lines_with_timestamp_command, hide=True)

    lines_with_timestamp = lines_with_timestamp_output.stdout.strip().split("\n")

    # Sanitize and combine the lines into a single string
    sanitized_lines = "\n".join(
        line.split("[Server thread/INFO]: ")[1] for line in lines_with_timestamp
    )

    # Send the sanitized and combined lines as a single message to Discord
    code_block = "```python\n" + sanitized_lines + "\n```"
    await ctx.send(code_block)


@client.command()
@commands.has_role("Server Op")
async def tps(ctx):
    shell = ctx.bot.extra_events["shell"]
    await ctx.send("Fetching server TPS...")

    # Execute ./minecraft_command.sh tps via SSH
    tps_command = "./minecraft_command.sh tps"
    try:
        shell.run(tps_command, hide=True)
    except Exception as e:
        print(f"An error occurred while running the command: {e}")
        pass

    # Read the logfile and extract the latest TPS line
    tps_grep = "grep TPS logs/latest.log | tail -n 1"
    line = shell.run(tps_grep, hide=True)  # Hide command output

    tps_line = line.stdout.strip()  # Get the stdout from the response
    await ctx.send("```python\n" + tps_line + "```")


@client.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member):
    role = get(ctx.guild.roles, name="Server Op")
    await member.add_roles(role)
    await ctx.send("Given " + member.mention + " the " + role.name + " role.")


@client.command()
@commands.has_role("Server Op")
async def status(ctx):
    shell = client.extra_events["shell"]
    await ctx.send("Returning server status!")
    status = str(shell.sudo("systemctl status minecraft.service | grep Active"))
    for line in status.split("\n"):
        if "Active" in line:
            await ctx.send("```python\n" + line + "```")


@client.command()
@commands.has_role("Server Op")
async def start(ctx):
    shell = client.extra_events["shell"]
    await ctx.send("Starting the server!")
    status = str(shell.sudo("systemctl start minecraft.service"))
    for line in status.split("\n"):
        if "with status 0" in line:
            await ctx.send("```python\n" + "Server has started successfully!" + "```")


@client.command()
@commands.has_role("Server Op")
async def restart(ctx):
    shell = client.extra_events["shell"]
    await ctx.send("Restarting the server!")
    status = str(shell.sudo("systemctl restart minecraft.service"))
    for line in status.split("\n"):
        if "with status 0" in line:
            await ctx.send("```python\n" + "Server has restarted successfully!" + "```")


@client.command()
@commands.has_role("Server Op")
async def stop(ctx):
    shell = client.extra_events["shell"]
    await ctx.send("Stopping the server!")
    status = str(shell.sudo("systemctl stop minecraft.service"))
    for line in status.split("\n"):
        if "with status 0" in line:
            await ctx.send("```python\n" + "Server has stopped successfully!" + "```")


@client.command()
@commands.has_role("Server Op")
async def wochelp(ctx):
    await ctx.send(
        "List of currently implemented commands\n"
        + "\n`!wochelp` - Displays this message\n"
        + "`!add @user` - Gives the mentioned user the Server Op role to use these commands\n"
        + "`!status` - Gives the current status of the server and uptime\n"
        + "`!start` - Starts the server if not running (does nothing if already running)\n"
        + "`!stop` - Stops the server if running (does nothing if already stopped)\n"
        + "`!restart` - Restarts the server, if running, starts the server if stopped\n"
        + "`!tps` - Gives the current TPS (Ticks Per Second) of the server. (20 is max)\n"
        + "\nContact @snipplerifsky for support or feature request!"
    )


@status.error
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingRole):
        role = get(ctx.guild.roles, name="Server Op")
        await ctx.send("Only the " + role.name + " role may use this command!")


@start.error
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingRole):
        role = get(ctx.guild.roles, name="Server Op")
        await ctx.send("Only the " + role.name + " role may use this command!")


@restart.error
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingRole):
        role = get(ctx.guild.roles, name="Server Op")
        await ctx.send("Only the " + role.name + " role may use this command!")


@stop.error
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingRole):
        role = get(ctx.guild.roles, name="Server Op")
        await ctx.send("Only the " + role.name + " role may use this command!")


@addrole.error
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingPermissions):
        await ctx.send("You do not have permissions to use this command")


client.run(BOTTOKEN)
