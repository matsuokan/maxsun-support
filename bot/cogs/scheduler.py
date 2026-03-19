"""
cogs/scheduler.py - 定期タスク（週次ランキング投稿・週次ポイントリセット）
"""
from __future__ import annotations

import datetime

import discord
import pytz
from discord.ext import commands, tasks

import config
from utils import sheets, helpers


class Scheduler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tz = pytz.timezone(config.TIMEZONE)
        self.weekly_task.start()

    def cog_unload(self):
        self.weekly_task.cancel()

    @tasks.loop(hours=1)
    async def weekly_task(self):
        """1時間ごとに実行し、曜日・時刻が一致したときに処理を走らせる。"""
        now = datetime.datetime.now(self.tz)
        weekday = now.strftime("%A").lower()  # 例: "monday"

        # 週次ランキング投稿
        if (
            weekday == config.RANKING_POST_DAY
            and now.hour == config.RANKING_POST_HOUR
            and now.minute < 60  # 1時間ループなので分は気にしない
        ):
            for guild in self.bot.guilds:
                await self.post_ranking(guild)

        # 週次ポイントリセット（ランキング投稿と同タイミング）
        if (
            weekday == config.WEEKLY_RESET_DAY
            and now.hour == config.RANKING_POST_HOUR
        ):
            sheets.reset_weekly_points()

    @weekly_task.before_loop
    async def before_weekly_task(self):
        await self.bot.wait_until_ready()

    async def post_ranking(self, guild: discord.Guild) -> None:
        """ランキングチャンネルにランキングを投稿する。"""
        ranking_ch = guild.get_channel(config.CHANNEL_RANKING)
        if ranking_ch is None:
            return

        top_total = sheets.get_leaderboard(limit=10)
        top_weekly = sheets.get_weekly_leaderboard(limit=10)

        medals = ["🥇", "🥈", "🥉"]

        def _format(records: list[dict], key: str) -> str:
            lines = []
            for i, m in enumerate(records, start=1):
                medal = medals[i - 1] if i <= 3 else f"**{i}.**"
                lines.append(f"{medal} {m['username']}　{m[key]} pt")
            return "\n".join(lines) if lines else "データなし"

        embed = discord.Embed(
            title="🏆 週次ランキング",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(self.tz),
        )
        embed.add_field(
            name="📊 今週の獲得ポイント Top 10",
            value=_format(top_weekly, "weekly_points"),
            inline=False,
        )
        embed.add_field(
            name="🌟 累計ポイント Top 10",
            value=_format(top_total, "total_points"),
            inline=False,
        )
        embed.set_footer(text="毎週日曜 0:00 JST 更新 | /mypoints で自分のポイントを確認")

        await ranking_ch.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Scheduler(bot))
