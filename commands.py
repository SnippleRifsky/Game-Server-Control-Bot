import discord
from client import init_client
from discord.utils import get
from discord.ext import commands

client = init_client()


@client.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member):
    role = get(ctx.guild.roles, name="Server Op")
    await member.add_roles(role)
    await ctx.send("Given "+member.mention+" the "+role.name+" role.")


@client.command()
@commands.has_role('Server Op')
async def status(ctx, shell):
    await ctx.send("Returning server status!")
    status = str(shell.sudo("systemctl status minecraft.service | grep Active"))
    for line in status.split('\n'):
        if 'Active' in line:
            await ctx.send("```python\n"+line+"```")


@client.command()
@commands.has_role('Server Op')
async def start(ctx, shell):
    await ctx.send("Starting the server!")
    status = str(shell.sudo("systemctl start minecraft.service"))
    for line in status.split('\n'):
        if 'with status 0' in line:
            await ctx.send("```python\n"+"Server has started successfully!"+"```")


@client.command()
@commands.has_role('Server Op')
async def restart(ctx, shell):
    await ctx.send("Restarting the server!")
    status = str(shell.sudo("systemctl restart minecraft.service"))
    for line in status.split('\n'):
        if 'with status 0' in line:
            await ctx.send("```python\n"+"Server has restarted successfully!"+"```")


@client.command()
@commands.has_role('Server Op')
async def stop(ctx, shell):
    await ctx.send("Stopping the server!")
    status = str(shell.sudo("systemctl stop minecraft.service"))
    for line in status.split('\n'):
        if 'with status 0' in line:
            await ctx.send("```python\n"+"Server has stopped successfully!"+"```")

@client.command()
@commands.has_role('Server Op')
async def help(ctx):
    await ctx.send("List of currently implemented commands\n"+
                   "\n`!help` - Displays this message\n"+
                   "`!add @user` - Gives the mentions user the Server Op role to use these commands\n"+
                   "`!status` - give the current status of the server and uptime\n"+
                   "`!start` - Starts the server if not running (does nothing if already running)\n"+
                   "`!stop` - Stops the server if running (does nothing if already stopped)\n"+
                   "`!restart` - Restarts the server, if running, starts the server if stopped\n"+
                   "\nContact @snipplerifsky for support or feature request!")