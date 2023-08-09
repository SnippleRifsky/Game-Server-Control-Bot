import discord
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

    # Execute the minecraft_command.sh "list"
    list_command = "./minecraft_command.sh list"

    try:
        shell.run(list_command, hide=True)
    except Exception as e:
        # Handle the exception here (print a message, log, etc.)
        print(f"An error occurred while running the command: {e}")
        pass

    # Get the latest line with "players online" from the logs
    latest_line_command = "grep 'players online' logs/latest.log* | tail -n 1"
    latest_line_output = shell.run(latest_line_command, hide=True)

    latest_line = latest_line_output.stdout.strip()

    # Extract timestamp from the latest line
    timestamp = latest_line.split("[")[1].split("]")[0]

    # Search for lines with the same timestamp in the logs
    lines_with_timestamp_command = (
        f"grep -h '[{timestamp}]' logs/latest.log* | grep -v '{latest_line}'"
    )
    lines_with_timestamp_output = shell.run(lines_with_timestamp_command, hide=True)

    lines_with_timestamp = lines_with_timestamp_output.stdout.strip()

    # Send all lines with the same timestamp to Discord
    await ctx.send("```\n" + lines_with_timestamp + "\n```")



@client.command()
@commands.has_role("Server Op")
async def tps(ctx):
    shell = ctx.bot.extra_events["shell"]
    await ctx.send("Fetching server TPS...")

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
