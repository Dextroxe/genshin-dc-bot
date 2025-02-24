import asyncio
from typing import Iterable, List

import aiohttp
import discord
from discord.ext import commands, tasks
from sqlalchemy import select

from common import conf
from common.constants import Preferences
from common.db import session
from common.logging import logger
from datamodels.code_redemption import RedeemableCode
from datamodels.genshin_user import GenshinUser
from datamodels.guild_settings import GuildSettings, GuildSettingKey


class GenshinCodeScanner(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.start_up = False

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.start_up:
            self.poll.start()
            self.start_up = True

    @tasks.loop(minutes=5)
    async def poll(self):
        if not conf.CODE_URL:
            return

        async with aiohttp.ClientSession() as http:
            async with http.get(conf.CODE_URL) as response:
                data = await response.read()
                codes = set(data.decode("utf-8").splitlines())

        existing_codes = set(
            session.execute(select(RedeemableCode.code)).scalars()
        )

        if codes.issubset(existing_codes):
            return

        logger.info("New code is available")

        new_codes = codes - existing_codes

        for code in new_codes:
            session.merge(RedeemableCode(code=code, working=True))

        for code in existing_codes - codes:
            session.merge(RedeemableCode(code=code, working=False))

        await self.send_notification(new_codes)
        await self.redeem(new_codes)
        session.commit()

    async def send_notification(self, codes: Iterable[str]):
        embed = discord.Embed(
            title="New codes available",
            description="\n".join(
                f"[{code}](https://genshin.hoyoverse.com/en/gift?code={code})"
                for code in codes
            )
        )

        for code_channel in session.execute(
                select(GuildSettings).where(
                    GuildSettings.key == GuildSettingKey.CODE_CHANNEL
                )
        ).scalars():
            try:
                channel = await self.bot.fetch_channel(code_channel.value)
                code_role = session.get(
                    GuildSettings,
                    (code_channel.guild_id, GuildSettingKey.CODE_ROLE),
                )
                await channel.send(
                    content=f"\n<@&{code_role.value}>" if code_role else None,
                    embed=embed,
                )
            except Exception:
                logger.exception("Cannot send new code notifications")

    async def redeem(self, codes: Iterable[str]):
        accounts: List[GenshinUser] = (
            session.execute(
                select(GenshinUser).where(GenshinUser.mihoyo_token.is_not(None))
            ).scalars().all()
        )

        for code in codes:
            queue = []
            for account in accounts:
                if not account.settings[Preferences.AUTO_REDEEM]:
                    continue
                logger.info(f"Redeeming code {code} for account {account.mihoyo_id}")
                queue.append(asyncio.create_task(account.client.redeem_code(code=code)))

            results = await asyncio.gather(*queue, return_exceptions=True)
            logger.info(results)
            await asyncio.sleep(5)
