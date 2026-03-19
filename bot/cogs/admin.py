"""
cogs/admin.py - 運営向けコマンド（MAXSUN 公式ロール限定）
"""
from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

import config
from utils import sheets, helpers


def is_staff():
    async def predicate(interaction: discord.Interaction) -> bool:
        staff_role = interaction.guild.get_role(config.ROLE_STAFF)
        if staff_role and staff_role in interaction.user.roles:
            return True
        await interaction.response.send_message(
            "❌ このコマンドは運営のみ使用できます。", ephemeral=True
        )
        return False
    return app_commands.check(predicate)


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── /add-points ───────────────────────────────
    @app_commands.command(name="add-points", description="【運営】ユーザーにポイントを手動加算します")
    @app_commands.describe(user="対象ユーザー", amount="加算ポイント数", reason="理由")
    @is_staff()
    async def add_points(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int,
        reason: str = "運営ボーナス",
    ):
        if amount <= 0:
            await interaction.response.send_message("❌ ポイントは 1 以上を指定してください。", ephemeral=True)
            return
        member_data = sheets.add_points(
            discord_id=str(user.id),
            username=user.display_name,
            delta=amount,
            action="bonus",
            note=reason,
        )
        total = member_data.get("total_points", "?") if member_data else "?"
        await interaction.response.send_message(
            f"✅ {user.mention} に **+{amount} pt** を付与しました。\n"
            f"理由: {reason}　累計: {total} pt",
            ephemeral=True,
        )
        # モデレーションログに記録
        mod_ch = interaction.guild.get_channel(config.CHANNEL_MOD_LOG)
        if mod_ch:
            await mod_ch.send(
                f"🔧 **ポイント手動加算**\n"
                f"対象: {user.mention}　+{amount} pt\n"
                f"実行者: {interaction.user.mention}　理由: {reason}"
            )

    # ── /remove-points ────────────────────────────
    @app_commands.command(name="remove-points", description="【運営】ユーザーのポイントをペナルティ減算します")
    @app_commands.describe(user="対象ユーザー", amount="減算ポイント数（正の数で入力）", reason="理由")
    @is_staff()
    async def remove_points(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int,
        reason: str = "規約違反",
    ):
        if amount <= 0:
            await interaction.response.send_message("❌ ポイントは 1 以上を指定してください。", ephemeral=True)
            return
        member_data = sheets.add_points(
            discord_id=str(user.id),
            username=user.display_name,
            delta=-amount,
            action="penalty",
            note=reason,
        )
        total = member_data.get("total_points", "?") if member_data else "?"
        await interaction.response.send_message(
            f"⚠️ {user.mention} から **{amount} pt** を減算しました。\n"
            f"理由: {reason}　累計: {total} pt",
            ephemeral=True,
        )
        mod_ch = interaction.guild.get_channel(config.CHANNEL_MOD_LOG)
        if mod_ch:
            await mod_ch.send(
                f"⚠️ **ポイントペナルティ**\n"
                f"対象: {user.mention}　−{amount} pt\n"
                f"実行者: {interaction.user.mention}　理由: {reason}"
            )

    # ── /userinfo ─────────────────────────────────
    @app_commands.command(name="userinfo", description="【運営】ユーザーのポイント・ランク詳細を確認します")
    @app_commands.describe(user="対象ユーザー")
    @is_staff()
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member):
        member_data = sheets.get_member(str(user.id))
        if member_data is None:
            await interaction.response.send_message(
                f"❌ {user.display_name} はまだ記録がありません。", ephemeral=True
            )
            return
        rank_display = helpers.rank_emoji(member_data["rank"])
        embed = discord.Embed(
            title=f"🔍 {user.display_name} の情報",
            color=discord.Color.orange(),
        )
        embed.add_field(name="Discord ID", value=member_data["discord_id"], inline=False)
        embed.add_field(name="ランク", value=rank_display, inline=True)
        embed.add_field(name="累計ポイント", value=f"{member_data['total_points']} pt", inline=True)
        embed.add_field(name="週間ポイント", value=f"{member_data['weekly_points']} pt", inline=True)
        embed.add_field(name="解決件数", value=f"{member_data['solved_count']} 件", inline=True)
        embed.add_field(name="👍 獲得数", value=f"{member_data['reaction_count']} 回", inline=True)
        embed.add_field(name="参加日時", value=member_data.get("joined_at", "不明"), inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── /reward-complete ──────────────────────────
    @app_commands.command(name="reward-complete", description="【運営】報酬発送完了をマークします")
    @app_commands.describe(user="報酬を発送したユーザー")
    @is_staff()
    async def reward_complete(self, interaction: discord.Interaction, user: discord.Member):
        # Google Sheets の rewards_log を手動で更新する旨を案内
        await interaction.response.send_message(
            f"📋 {user.mention} への報酬発送完了を記録します。\n"
            f"Google Sheets の `rewards_log` シートで該当行の `status` を `shipped` → `completed` に更新してください。\n"
            f"ユーザーへの通知も忘れずに！",
            ephemeral=True,
        )
        mod_ch = interaction.guild.get_channel(config.CHANNEL_MOD_LOG)
        if mod_ch:
            await mod_ch.send(
                f"📦 **報酬発送完了処理**\n"
                f"対象: {user.mention}\n"
                f"実行者: {interaction.user.mention}\n"
                f"→ Sheets の rewards_log を更新してください。"
            )

    # ── /post-ranking ─────────────────────────────
    @app_commands.command(name="post-ranking", description="【運営】週次ランキングを今すぐ投稿します")
    @is_staff()
    async def post_ranking(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        scheduler_cog = self.bot.cogs.get("Scheduler")
        if scheduler_cog:
            await scheduler_cog.post_ranking(interaction.guild)
            await interaction.followup.send("✅ ランキングを投稿しました。", ephemeral=True)
        else:
            await interaction.followup.send("❌ Scheduler Cog が見つかりません。", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
