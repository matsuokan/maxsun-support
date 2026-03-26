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
    "cogs.setup",
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
        # 起動時: 未投稿チャンネルへの自動投稿
        await self._auto_post_pending()

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

    async def _auto_post_pending(self):
        """起動時に未投稿のチャンネルへコンテンツを自動投稿"""
        from cogs.setup import CHANNEL_CONTENT

        for guild in self.guilds:
            for ch_name, messages in CHANNEL_CONTENT.items():
                # チャンネルを名前で検索
                channel = discord.utils.get(guild.text_channels, name=ch_name)
                if channel is None:
                    continue
                # メッセージ履歴を確認（既に投稿済みならスキップ）
                history = [m async for m in channel.history(limit=1)]
                if history:
                    continue
                # 空のチャンネルに投稿
                try:
                    for msg in messages:
                        await channel.send(msg)
                    logger.info(f"Auto-posted to #{ch_name} ({len(messages)} msgs)")
                except Exception as e:
                    logger.error(f"Failed to auto-post to #{ch_name}: {e}")


async def main():
    bot = MaxBot()
    async with bot:
        await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
