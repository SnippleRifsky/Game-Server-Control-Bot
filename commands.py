import discord
import time
from fabric import exceptions as fabric_exceptions
from invoke import exceptions as invoke_exceptions
from client import init_client
from discord.utils import get
from discord.ext import commands

client = init_client()


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
async def lpedit(ctx):
    shell = ctx.bot.extra_events["shell"]

    # Execute ./minecraft_command.sh 'lp editor' via SSH
    lpedit_command = "./minecraft_command.sh 'lp editor'"
    try:
        shell.run(lpedit_command, hide=True)
    except Exception as e:
        print(f"An error occurred while running the command: {e}")
        pass

    time.sleep(1)

    # Find the last occurrence of new lp editor session in the logs
    last_lpedit_command = (
        "grep 'Preparing a new editor session' logs/latest.log* | tail -n 1"
    )
    last_lpedit_output = shell.run(last_lpedit_command, hide=True)

    last_lpedit_line = last_lpedit_output.stdout.strip()

    # Send the last_lpedit_line and the next 2 lines after it to Discord
    formatted_message = f"```\n{last_lpedit_line}\n"

    # Add line containing editor link
    editor_link = shell.run("tail -n 1 logs/latest.log*", hide=True).stdout.strip()
    formatted_message += f"{editor_link}\n```"

    # Sanitize and format the output
    sanitized_lines = [line.replace("[12:41:52] [luckperms-command-executor/INFO]:", "") for line in hardcoded_lines.split("\n")]
    formatted_message = "```python\n"
    formatted_message += last_lpedit_line + "\n"
    formatted_message += "\n".join(sanitized_lines) + "\n"
    formatted_message += "```"

    await ctx.send(formatted_message)


@client.command()
@commands.has_role("Server Op")
async def tps(ctx):
    shell = ctx.bot.extra_events["shell"]
    await ctx.send("Fetching server TPS...")

    # Execute ./minecraft_command.sh tps via SSH
    list_command = "./minecraft_command.sh tps"
    try:
        shell.run(list_command, hide=True)
    except Exception as e:
        print(f"An error occurred while running the command: {e}")
        pass

    # Read the logfile and extract the latest TPS line
    tps_command = "grep 'TPS' logs/latest.log | tail -n 1"
    line = shell.run(tps_command, hide=True)  # Hide command output

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
async def status(ctx, shell):
    shell = client.extra_events["shell"]
    await ctx.send("Returning server status!")
    status = str(shell.sudo("systemctl status minecraft.service | grep Active"))
    for line in status.split("\n"):
        if "Active" in line:
            await ctx.send("```python\n" + line + "```")


@client.command()
@commands.has_role("Server Op")
async def start(ctx, shell):
    shell = client.extra_events["shell"]
    await ctx.send("Starting the server!")
    status = str(shell.sudo("systemctl start minecraft.service"))
    for line in status.split("\n"):
        if "with status 0" in line:
            await ctx.send("```python\n" + "Server has started successfully!" + "```")


@client.command()
@commands.has_role("Server Op")
async def restart(ctx, shell):
    shell = client.extra_events["shell"]
    await ctx.send("Restarting the server!")
    status = str(shell.sudo("systemctl restart minecraft.service"))
    for line in status.split("\n"):
        if "with status 0" in line:
            await ctx.send("```python\n" + "Server has restarted successfully!" + "```")


@client.command()
@commands.has_role("Server Op")
async def stop(ctx, shell):
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
