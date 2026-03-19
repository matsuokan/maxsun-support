"""
cogs/info.py - /mypoints・/leaderboard・/faq コマンド
"""
from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils import sheets, helpers


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── /mypoints ─────────────────────────────────
    @app_commands.command(name="mypoints", description="自分の累計ポイントとランクを確認します")
    async def mypoints(self, interaction: discord.Interaction):
        member_data = sheets.get_member(str(interaction.user.id))
        if member_data is None:
            await interaction.response.send_message(
                "まだポイントが記録されていません。サポートチャンネルで回答してポイントを稼ぎましょう！",
                ephemeral=True,
            )
            return

        rank_display = helpers.rank_emoji(member_data["rank"])
        progress = helpers.format_rank_bar(member_data["total_points"])

        embed = discord.Embed(
            title=f"📊 {interaction.user.display_name} のポイント情報",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="現在のランク", value=rank_display, inline=True)
        embed.add_field(name="累計ポイント", value=f"{member_data['total_points']} pt", inline=True)
        embed.add_field(name="今週獲得", value=f"{member_data['weekly_points']} pt", inline=True)
        embed.add_field(name="解決件数", value=f"{member_data['solved_count']} 件", inline=True)
        embed.add_field(name="👍 獲得数", value=f"{member_data['reaction_count']} 回", inline=True)
        embed.add_field(name="次のランクまで", value=progress, inline=False)
        embed.set_footer(text="回答してポイントを貯めよう！ /solved で +20 pt")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── /leaderboard ──────────────────────────────
    @app_commands.command(name="leaderboard", description="累計ポイントランキング Top10 を表示します")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        top = sheets.get_leaderboard(limit=10)
        if not top:
            await interaction.followup.send("まだランキングデータがありません。", ephemeral=True)
            return

        lines = []
        medals = ["🥇", "🥈", "🥉"]
        for i, m in enumerate(top, start=1):
            medal = medals[i - 1] if i <= 3 else f"**{i}.**"
            lines.append(
                f"{medal} {m['username']}　{m['total_points']} pt "
                f"（{helpers.rank_emoji(m['rank'])}）"
            )

        embed = discord.Embed(
            title="🏆 累計ポイントランキング Top 10",
            description="\n".join(lines),
            color=discord.Color.gold(),
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    # ── /faq ──────────────────────────────────────
    @app_commands.command(name="faq", description="キーワードで FAQ を検索します")
    @app_commands.describe(keyword="検索キーワード（例: BIOS、POST失敗）")
    async def faq(self, interaction: discord.Interaction, keyword: str):
        await interaction.response.defer(ephemeral=True)
        results = sheets.search_faq(keyword)
        if not results:
            await interaction.followup.send(
                f"「{keyword}」に一致する FAQ が見つかりませんでした。\n"
                "サポートチャンネルで質問してみましょう！",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"🔍 FAQ 検索結果：「{keyword}」",
            color=discord.Color.green(),
        )
        for r in results:
            embed.add_field(
                name=f"[{r['faq_id']}] {r['question']}",
                value=r["answer"][:500] + ("..." if len(r["answer"]) > 500 else ""),
                inline=False,
            )
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
