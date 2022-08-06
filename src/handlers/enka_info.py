import discord
import asyncio
from discord.ext import commands
from utils import Enka

class game_infoHandler(commands.Cog):
    def __init__(self, bot: discord.Bot = None):
        self.bot = bot

    @commands.slash_command(
    # name='profile_characters', 
    description='Query the public character showcase of the player with the specified UID'
    )

    # enka-network
    async def profile_characters(self, ctx: discord.ApplicationContext, uid: int):
        # interaction: discord.Interaction
        asyncio.create_task(ctx.response.defer())
        if uid == None:
            await ctx.edit(content='The user information cannot be found in the little helper, please directly enter the UID to be queried in the command uid parameter')
        elif len(str(uid)) != 9 or str(uid)[0] not in ['1', '2', '5', '6', '7', '8', '9']:
            await ctx.edit(content='The entered UID is in the wrong format')
        else:
            showcase = Enka.Showcase()
            try:
                await showcase.getEnkaData(uid)
            except Enka.ShowcaseNotPublic as e:
                embed = showcase.getPlayerOverviewEmbed()
                embed.description += f"\n{e}"
                await ctx.edit(embed=embed)
            except Exception as e:
                await ctx.edit(content=f"{e}")
            else:
                view = Enka.ShowcaseView(showcase)
                embed = showcase.getPlayerOverviewEmbed()
                await ctx.edit(embed=embed, view=view)
                await view.wait()
                await ctx.edit(view=None)

