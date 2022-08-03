import discord
import asyncio
import genshin
# from discord import app_commands
from typing import List
from discord.ext import commands
# from utils.GenshinApp import genshin_app
from utils.draw import drawRecordCard, drawAbyssCard
# from discord.app_commands import Choice
from typing import Union
# from utils.config import config
# from utils.emoji import emoji
from utils.game_notes import getCharacterName
slash_cmd_cooldown: float = 5.0




class abyssHandler(commands.Cog):
    def __init__(self, bot: discord.Bot = None):
        self.bot = bot

     # Abyss Records
    @commands.slash_command(
    # name='abyss-craft', 
    description='Query the public character showcase of the player with the specified UID'
    )
    # @app_commands.checks.cooldown(1, slash_cmd_cooldown)

    @discord.ui.select( placeholder = 'Select Option',
                    custom_id = 'activitySelect',
                    options =   [
                                    discord.SelectOption(label ='period',value='period'),
                                    discord.SelectOption(label='floor',value='floor')
                                ]
                  )
    # @discord.ui.select(
    #     season='Select current or previous record',
    #     floor='Select the display method of floor person records')
    # @discord.ui.select(
    #     season=[discord.SelectOption(label='Previous abyss cycle', value=0),discord.SelectOption(name='Latest abyss cycle', value=1)],
    #      floor=[discord.SelectOption(label='Show all floors', value=0),discord.SelectOption(name='Show last floor', value=1)]
    
    #             ) 

    async def slash_abyss(self, ctx: discord.ApplicationContext):
        season: int = 1
        floor: int = 2
        asyncio.create_task(ctx.response.defer())
        previous = True if season == 0 else False
        result = await self.getSpiralAbyss(str(ctx.user.id), previous)
        if isinstance(result, str):
            await ctx.edit(content=result)
            return

        embed = self.parseAbyssOverview(result)
        embed.title = f'{ctx.user.display_name} Spiral Abyss Info'
        if floor == 0: # [text] show all floors
            embed = self.parseAbyssFloor(embed, result, True)

            embed.set_image(url="https://theclick.gg/wp-content/uploads/2021/07/Spiral_Abyss-genshin.png")
            embed.set_thumbnail(url="https://theclick.gg/wp-content/uploads/2021/07/Spiral_Abyss-genshin.png")
            embed.set_footer (text='``Challenge different floors of the tower and defeat the enemies within to win Abyssal Stars. Do this, and the Spiral Abyss may yet look upon your hard work and bestow rewards upon you.``',icon_url="https://theclick.gg/wp-content/uploads/2021/07/Spiral_Abyss-genshin.png")
            await ctx.edit(embed=embed)
        # elif floor == 1: # [text] only show the last layer
        #     embed = genshin_app.parseAbyssFloor(embed, result, False)
            await ctx.edit(embed=embed)
        elif floor == 1: # [image] only show the last layer``
            try:
                fp = drawAbyssCard(result)
            except Exception as e:
                # log.error(f'[exception][{ctx.user.id}][slash_abyss]: {e}')
                await ctx.edit(content='An error occurred, image creation failed')
            else:
                embed.set_thumbnail(url=ctx.user.display_avatar.url)
                fp.seek(0)
                file = discord.File(fp, filename='image.jpeg')
                embed.set_image(url='attachment://image.jpeg')
                await ctx.edit(embed=embed, attachments=[file])


    async def getSpiralAbyss(self, user_id: str, previous: bool = False) -> Union[str, genshin.models.SpiralAbyss]:
        """Get Spiral Abyss information

        ------
       Parameters
         user_id `str`: User Discord ID
         previous `bool`: `True` to query the information of the previous issue, `False` to query the information of the current issue
         ------
         Returns
         `Union[str, SpiralAbyss]`: return error message `str` when exception occurs, return query result `SpiralAbyss` under normal conditions
        """
        # log.info(
        #     f'[instruction][{user_id}]getSpiralAbyss: previous={previous}')
        check, msg = self.checkUserData(user_id)
        if check == False:
            return msg
        client = self.__getGenshinClient(user_id)
        try:
            abyss = await client.get_genshin_spiral_abyss(int(self.__user_data[user_id]['uid']), previous=previous)
        except genshin.errors.GenshinException as e:
            # log.error(
            #     f'[exception][{user_id}]getSpiralAbyss: [retcode]{e.retcode} [Exceptions]{e.original}')
            return e.original
        except Exception as e:
            # log.error(f'[exception][{user_id}]getSpiralAbyss: [Exceptions]{e}')
            return f'{e}'
        else:
            return abyss
    
    def parseAbyssOverview(self, abyss: genshin.models.SpiralAbyss) -> discord.Embed:
        """Analyze the abyss overview data, including date, number of layers, number of battles, total number of stars...etc.

         ------
         Parameters
         abyss `SpiralAbyss`: Deep Spiral Information
         ------
         Returns
         `discord.Embed`: discord embed format
        """
        result = discord.Embed(
            description=f'Info of Abyss cycle -> {abyss.season}th cycle    &    Date: {abyss.start_time.astimezone().strftime("%Y.%m.%d")} to {abyss.end_time.astimezone().strftime("%Y.%m.%d")}', color=0x6959c1)
        def get_char(c): return ' ' if len(
            c) == 0 else f'{getCharacterName(c[0])}: {c[0].value}'
        result.add_field(
            name=f'Deepest descension: {abyss.max_floor}, Battles: {"👑" if abyss.total_stars == 36 and abyss.total_battles == 12 else abyss.total_battles}, ★ earned: {abyss.total_stars}',
            value=f'[mobs defeats] {get_char(abyss.ranks.most_kills)}\n'
            f'[highest damage dealt] {get_char(abyss.ranks.strongest_strike)}\n'
            f'[highest damage taken] {get_char(abyss.ranks.most_damage_taken)}\n'
            f'[Burst unleashed] {get_char(abyss.ranks.most_bursts_used)}\n'
            f'[Skill casts] {get_char(abyss.ranks.most_skills_used)}',
            inline=False
        )
        return result

    def parseAbyssFloor(self, embed: discord.Embed, abyss: genshin.models.SpiralAbyss, full_data: bool = False) -> discord.Embed:
        """Analyze each floor of the abyss, add the number of stars on each floor and the character data used to the embed

         ------
         Parameters
         embed `discord.Embed`: Embed data obtained from the `parseAbyssOverview` function
         abyss `SpiralAbyss`: Deep Spiral Information
         full_data `bool`: `True` means parsing all floors; `False` means parsing only the last level
         ------
         Returns
         `discord.Embed`: discord embed format
        """

        for floor in abyss.floors:
            if full_data == False and floor is not abyss.floors[-1]:
                continue
            for chamber in floor.chambers:
                name = f'{floor.floor}-{chamber.chamber} ★{chamber.stars}'
                # Get the character name of the upper and lower half layers of the abyss
                chara_list = [[], []]
                for i, battle in enumerate(chamber.battles):
                    for chara in battle.characters:
                        chara_list[i].append(getCharacterName(chara))
                value = f'[{",".join(chara_list[0])}] || \n[{",".join(chara_list[1])}]\n'
                embed.add_field(name=name, value=value)
        return embed
    
    # @slash_abyss.error
    # async def on_slash_abyss_error(self, ctx: discord.ApplicationContext, error: commands.AppCommandError):
    #     if isinstance(error, commands.CommandOnCooldown):
    #         await ctx.response.send_message(f'The interval for using the command is {slash_cmd_cooldown}seconds, please try again later~', ephemeral=True)