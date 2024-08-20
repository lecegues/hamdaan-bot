import discord
from discord.ext import commands


class GeneralCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="help", description="Shows all commands.")
    async def help(self, ctx):
        '''Show all commands in a code block'''
        command_list = [
            f"/{command.name} - {command.description}"
            for command in self.bot.commands
        ]
        command_text = "\n".join(command_list)
        await ctx.respond(f"```\n{command_text}\n```")


def setup(bot):
    bot.add_cog(GeneralCog(bot))
