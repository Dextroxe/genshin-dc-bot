
import discord
import asyncio
# import genshin

from typing import Optional
from discord.ext import commands
# from utils.GenshinApp import genshin_app
# from utils.draw import drawRecordCard, drawAbyssCard
# from discord.commands import Choice
# from typing import Sequence, Union, Tuple
# from utils.config import config
# from utils.emoji import emoji
# from spiral_abyss import getCharacterName
from utils import Enka
# slash_cmd_cooldown: float = 5.0

class game_infoHandler(commands.Cog):
    def __init__(self, bot: discord.Bot = None):
        self.bot = bot

    @commands.slash_command(
    # name='profile_characters', 
    description='Query the public character showcase of the player with the specified UID'
    )

    # enka-network
    async def profile_characters(self, ctx: discord.ApplicationContext,uid: Optional[int] = None):
        # interaction: discord.Interaction, 
        asyncio.create_task(ctx.response.defer())
        # uid = uid or genshin_app.getUID(str(interaction.user.id))
        # log.info(f'[instruction][{interaction.user.id}]character showcase: uid={uid}')
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
                # log.info(f'[exception][{interaction.user.id}] Character Showcase: {e}')
            else:
                view = Enka.ShowcaseView(showcase)
                embed = showcase.getPlayerOverviewEmbed()
                await ctx.edit(embed=embed, view=view)
                await view.wait()
                await ctx.edit(view=None)

