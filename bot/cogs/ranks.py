"""
cogs/ranks.py - ランク管理（手動昇格チェック用）
ranks.py は主に Points cog の _check_rank_up から呼ばれる。
このファイルでは /rank コマンドを提供する。
"""
from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

import config
from utils import sheets, helpers


class Ranks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="rank", description="指定ユーザーのランク情報を表示します（運営向け）")
    @app_commands.checks.has_role(config.ROLE_STAFF)
    async def rank_info(self, interaction: discord.Interaction, user: discord.Member):
        member_data = sheets.get_member(str(user.id))
        if member_data is None:
            await interaction.response.send_message(
                f"❌ {user.display_name} はまだコミュニティに記録がありません。",
                ephemeral=True,
            )
            return
        rank_display = helpers.rank_emoji(member_data["rank"])
        progress = helpers.format_rank_bar(member_data["total_points"])
        embed = discord.Embed(
            title=f"📊 {user.display_name} のランク情報",
            color=discord.Color.gold(),
        )
        embed.add_field(name="現在のランク", value=rank_display, inline=True)
        embed.add_field(name="累計ポイント", value=f"{member_data['total_points']} pt", inline=True)
        embed.add_field(name="週間ポイント", value=f"{member_data['weekly_points']} pt", inline=True)
        embed.add_field(name="解決件数", value=f"{member_data['solved_count']} 件", inline=True)
        embed.add_field(name="次のランクまで", value=progress, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Ranks(bot))
