from logging import exception
import aiohttp
import discord
from typing import Any, Dict, List, Union, Optional
from utils.emoji import emoji
from data.game.characters import characters_map
from data.game.weapons import weapons_map
from data.game.artifacts import artifcats_map
from data.game.fight_prop import fight_prop_map, get_prop_name

class ShowcaseNotPublic(Exception):
    def __init__(self, message: str) -> None:
        self.__init__
        (message)

class Showcase:
    data: Dict[str, Any] = None
    uid: int = 0
    url: str = ''

    def __init__(self) -> None:
        pass

    async def getEnkaData(self, uid: int) -> None:
        """Get the character showcase data of the player with the specified UID from the API"""
        self.uid = uid
        self.url = f'https://enka.shinshin.moe/u/{uid}'
        async with aiohttp.request('GET', self.url + '/__data.json') as resp:
            if resp.status == 200:
                self.data = await resp.json()
                if 'avatarInfoList' not in self.data:
                    raise ShowcaseNotPublic("The in-game character showcase is not enble for public")
            elif resp.status == 500:
                raise Exception("This UID player profile does not exist")
            else:
                raise Exception("Failed to get API data")

    def getPlayerOverviewEmbed(self) -> discord.Embed:
        """Embed message to get player's basic data"""
        player: Dict[str, Any] = self.data['playerInfo']
        embed = discord.Embed(
            title=player.get('nickname', str(self.uid)),
            description=
                f"   **「 {player.get('signature', '')} 」**\n"
                f"<:Combat:992058814247485500> **Adventure Rank: **{player.get('level', 1)}\n"
                f"<:archon_quest:992062501346873394> **World Level: **{player.get('worldLevel', 0)}\n"
                f"<:exp:987399117418401842> **Total Achievements: **{player.get('finishAchievementNum', 0)}\n"
                f"<:Spiral_Abyss:992061853062668368> **Spiral Abyss: **{player.get('towerFloorIndex', 0)}-{player.get('towerLevelIndex', 0)}"
        )
        if 'profilePicture' in player and 'avatarId' in player['profilePicture']:
            icon = characters_map[str(player['profilePicture']['avatarId'])]['icon']
            embed.set_thumbnail(url=icon)
            embed.set_author(name="Enka.network",url="https://enka.shinshin.moe/",icon_url="https://pbs.twimg.com/profile_images/1504685226072719370/lmLkMCH5_400x400.png")
            embed.set_footer(text=f'UID: {self.uid}')
            embed.set_image(url="https://i.ytimg.com/vi/ktyaN2M0rfM/maxresdefault.jpg")
            embed.set_footer(text="Following Embed is using the Enka.network API to give you such result",icon_url="https://enka.shinshin.moe/")
        return embed

    def getCharacterStatEmbed(self, index: int) -> discord.Embed:
        """Get embed message for character panel"""
        avatarInfo: Dict[str, Any] = self.data['avatarInfoList'][index]
        id = str(avatarInfo['avatarId'])
        embed = self.__getDefaultEmbed(id)
        embed.title += ' Stats'

        # Talent Level [A, E, Q]
        skill_level = [0, 0, 0]
        for i in range(3):
            if 'skillOrder' in characters_map[id]:
                skillId = characters_map[id]['skillOrder'][i]
            else:
                skillId = list(avatarInfo['skillLevelMap'])[i]
            skill_level[i] = avatarInfo['skillLevelMap'][str(skillId)]
        # basic information
        embed.add_field(
            name=f"character_information",
            value=f"<:Stella_Fortuna:992060189958230076> **Constellation:** {0 if 'talentIdList' not in avatarInfo else len(avatarInfo['talentIdList'])}\n"
                  f"<:Ascension:992059222013521953> **Level: Lv.** {avatarInfo['propMap']['4001']['val']}\n"
                  f"<:talent:992060993540734987> **Talent:** {skill_level[0]}/{skill_level[1]}/{skill_level[2]}\n"
                  f"<:Character:992058802440515584> **Friendship: Lv.** {avatarInfo['fetterInfo']['expLevel']}",
        )
        # arms
        equipList: List[Dict[str, Any]] = avatarInfo['equipList']
        if 'weapon' in equipList[-1]:
            weapon = equipList[-1]
            weaponStats = weapon['flat']['weaponStats']
            refinement = 1
            if 'affixMap' in weapon['weapon']:
                refinement += list(weapon['weapon']['affixMap'].values())[0]
            embed.add_field(
                name=f"★{weapon['flat']['rankLevel']} {weapons_map[weapon['itemId']]['name']}",
                value=f"<:Combat:992058814247485500> **Refinement:** {refinement}\n"
                      f"<:Ascension:992059222013521953> **Level:** {weapon['weapon']['level']}\n"
                      f"{emoji.fightprop.get('FIGHT_PROP_ATTACK', '')} **base attack** +{weaponStats[0]['statValue']}\n"
                      f"{self.__getStatPropSentence(weaponStats[1]['appendPropId'], weaponStats[1]['statValue'])}"
            )
        # character Information
        prop: Dict[str, float] = avatarInfo['fightPropMap']
        substat: str = '\n'.join([self.__getCharacterFightPropSentence(int(id), prop[id]) for
            id in ['20', '22', '28', '26', '23', '30', '40', '41', '42', '43', '44', '45', '46'] if prop[id] > 0])
        embed.add_field(
            name='character_info',
            value=f"{emoji.fightprop.get('FIGHT_PROP_HP','')} HP: {round(prop['2000'])} ({round(prop['1'])} +{round(prop['2000'])-round(prop['1'])})\n"
                  f"{emoji.fightprop.get('FIGHT_PROP_ATTACK','')} Attack : {round(prop['2001'])} ({round(prop['4'])} +{round(prop['2001'])-round(prop['4'])})\n"
                  f"{emoji.fightprop.get('FIGHT_PROP_DEFENSE','')} Defense: {round(prop['2002'])} ({round(prop['7'])} +{round(prop['2002'])-round(prop['7'])})\n"
                  f"{substat}",
            inline=False
        )
        return embed
    
    def getArtifactStatEmbed(self, index: int) -> discord.Embed:
        """Get the embedded message of the character's relic"""
        avatarInfo: Dict[str, Any] = self.data['avatarInfoList'][index]
        id = str(avatarInfo['avatarId'])
        embed = self.__getDefaultEmbed(id)
        embed.title += ' Artifacts'
        
        # paste the id of the artifact emojis
        #---------
        flower = '<:flower:1004237691417804900> '
        feather = '<:Plume:1004238476323078194> '
        sands = '<:Sands:1004238484057378856> '
        goblet = '<:Goblet:1004238481553379418> '
        circlet = '<:Circlet:1004238478420226131> '
        #----------

        pos_name_map = {1: flower, 2: feather, 3: sands, 4: goblet, 5: circlet}
        substat_sum: Dict[str, float] = dict() # Count of adverbs
        
        equip: Dict[str, Any]
        for equip in avatarInfo['equipList']:
            if 'reliquary' not in equip:
                continue
            artifact_id: int = equip['itemId'] // 10
            flat = equip['flat']
            pos_name = pos_name_map[artifcats_map[artifact_id]['pos']]

            # main entry attribute
            embed_value = f"{self.__getStatPropSentence(flat['reliquaryMainstat']['mainPropId'], flat['reliquaryMainstat']['statValue'])}\n"

            # Adverb entry attribute
            for substat in flat['reliquarySubstats']:
                prop: str = substat['appendPropId']
                value: Union[int, float] = substat['statValue']
                embed_value += f"{self.__getStatPropSentence(prop, value)}\n"
                substat_sum[prop] = substat_sum.get(prop, 0) + value
            
            embed.add_field(name=f"{pos_name}: {artifcats_map[artifact_id]['name']}", value=embed_value)

        # Count of adverbs
        def substatSummary(prop: str, name: str, base: float) -> str:
            return f"{emoji.fightprop.get(prop, '')}{name}: {round(value / base, 1)}\n" if (value := substat_sum.get(prop)) != None else ''
        
        embed_value = ''
        embed_value += substatSummary('FIGHT_PROP_ATTACK_PERCENT', '  Attack % ', 5.0)
        embed_value += substatSummary('FIGHT_PROP_HP_PERCENT', '  HP % ', 5.0)
        embed_value += substatSummary('FIGHT_PROP_DEFENSE_PERCENT', '  Defense % ', 6.2)
        embed_value += substatSummary('FIGHT_PROP_CHARGE_EFFICIENCY', '  **Energy Rechange** ', 5.5)
        embed_value += substatSummary('FIGHT_PROP_ELEMENT_MASTERY', '  **Elemental Mastery** ', 20)
        embed_value += substatSummary('FIGHT_PROP_CRITICAL', '  **Crit Rate** ', 3.3)
        embed_value += substatSummary('FIGHT_PROP_CRITICAL_HURT', '  **Crit Damage** ', 6.6)
        if embed_value != '':
            embed.add_field(name=' **Count of adverbs** ', value=embed_value)
        
        return embed

    def __getDefaultEmbed(self, character_id: str) -> discord.Embed:
        id = character_id
        color = {'pyro': 0xfb4120, 'electro': 0xbf73e7, 'hydro': 0x15b1ff, 'cryo': 0x70daf1, 'dendro': 0xa0ca22, 'anemo': 0x5cd4ac, 'geo': 0xfab632}
        embed = discord.Embed(
            title=f"{characters_map[id]['rarity']}★ {characters_map[id]['name']}",
            color=color.get(characters_map[id]['element'].lower())
        )
        embed.set_thumbnail(url=characters_map[id]['icon'])
        embed.set_author(name=f"{self.data['playerInfo']['nickname']}'s character from (enka.network)", url=self.url,icon_url="https://pbs.twimg.com/profile_images/1504685226072719370/lmLkMCH5_400x400.png")
        embed.set_footer(text=f"{self.data['playerInfo']['nickname']}. Lv. {self.data['playerInfo']['level']}. UID: {self.uid}")

        return embed

    def __getCharacterFightPropSentence(self, prop: int, value: Union[int, float]) -> str:
        emoji_str = emoji.fightprop.get(fight_prop_map.get(prop), '')
        prop_name = get_prop_name(prop)
        if '%' in prop_name:
            return emoji_str + prop_name.replace('%', f': {round(value * 100, 1)}%')
        return emoji_str + prop_name + f': {round(value)}'

    def __getStatPropSentence(self, prop: str, value: Union[int, float]) -> str:
        emoji_str = emoji.fightprop.get(prop, '')
        prop_name = get_prop_name(prop)
        if '%' in prop_name:
            return emoji_str + prop_name.replace('%', f'+{value}%')
        return emoji_str + prop_name + f'+{value}'


class ShowcaseCharactersDropdown(discord.ui.Select):
    """Showcase role drop-down menu"""
    showcase: Showcase
    
    def __init__(self, showcase: Showcase) -> None:
        self.showcase = showcase
        avatarInfoList: List[Dict[str, Any]] = showcase.data["avatarInfoList"]
        options = []
        for i, avatarInfo in enumerate(avatarInfoList):
            id = str(avatarInfo['avatarId'])
            level: str = avatarInfo['propMap']['4001']['val']
            rarity: int = characters_map[id]['rarity']
            element: str = characters_map[id]['element']
            name: str = characters_map[id]['name']
            options.append(discord.SelectOption(
                label=f'{rarity}★ Lv.{level} {name}',
                value=str(i),
                emoji=emoji.elements.get(element.lower())
            ))
        super().__init__(placeholder=f'Find a showcase character:', options=options)
class CharacterStatButton(discord.ui.Button):
    """Character panel buttons"""
    showcase: Showcase
    character_index: int

    def __init__(self, showcase: Showcase, character_index: int):
        super().__init__(style=discord.ButtonStyle.green, label='character stats')
        self.showcase = showcase
        self.character_index = character_index
    
    async def callback(self, interaction: discord.Interaction) -> Any:
        embed = self.showcase.getCharacterStatEmbed(self.character_index)
        await interaction.response.edit_message(embed=embed)

class CharacterArtifactButton(discord.ui.Button):
    """Character Artifact button"""
    showcase: Showcase
    character_index: int
    def __init__(self, showcase: Showcase, character_index: int):
        super().__init__(style=discord.ButtonStyle.primary, label='Artifacts')
        self.showcase = showcase
        self.character_index = character_index
    
    async def callback(self, interaction: discord.Interaction) -> Any:
        embed = self.showcase.getArtifactStatEmbed(self.character_index)
        await interaction.response.edit_message(embed=embed)

class ShowcaseView(discord.ui.View):
    """Character showcase view, showing character panel, Artifact button, and character drop-down menu"""
    def __init__(self, showcase: Showcase, character_index: Optional[int] = None):
        super().__init__(timeout=600)
        if character_index != None:
            self.add_item(CharacterStatButton(showcase, character_index))
            self.add_item(CharacterArtifactButton(showcase ,character_index))
            self.add_item(ShowcaseCharactersDropdown(showcase))  