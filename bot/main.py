"""
main.py - Discord Bot エントリーポイント
"""
from __future__ import annotations

import asyncio
import logging

import discord
from discord.ext import commands

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("maxbot")

COGS = [
    "cogs.points",
    "cogs.support",
    "cogs.ranks",
    "cogs.rewards",
    "cogs.info",
    "cogs.admin",
    "cogs.scheduler",
]


class MaxBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.reactions = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        for cog in COGS:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")

        # スラッシュコマンドをグローバルに同期
        synced = await self.tree.sync()
        logger.info(f"Synced {len(synced)} slash command(s)")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="MAXSUN サポートコミュニティ",
            )
        )

    async def on_command_error(self, ctx, error):
        logger.error(f"Command error: {error}")

    async def on_application_command_error(
        self, interaction: discord.Interaction, error: Exception
    ):
        logger.error(f"App command error: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "⚠️ エラーが発生しました。しばらく経ってからもう一度お試しください。",
                ephemeral=True,
            )


async def main():
    bot = MaxBot()
    async with bot:
        await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
