"""
cogs/support.py - /solved コマンド・フォーラム質問テンプレート自動投稿
"""
from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

import config
from utils import sheets, helpers
from cogs.points import Points

QUESTION_TEMPLATE = """📋 **質問テンプレート**

回答者が理解しやすいよう、以下を埋めてください：

┌────────────────────────────
■ **製品名・型番**：（例: MS-RX7900XT GAMING X 24G）
■ **OS・バージョン**：（例: Windows 11 23H2）
■ **症状・問題**：
■ **試したこと**：
■ **エラーメッセージ**（あれば）：
└────────────────────────────

解決したら `/solved` コマンドを実行してください ✅
"""


class Support(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── フォーラムスレッド作成時に質問テンプレートを自動投稿 ──
    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        parent_id = thread.parent_id
        if parent_id not in config.SUPPORT_FORUM_CHANNEL_IDS:
            return
        try:
            await thread.send(QUESTION_TEMPLATE)
        except discord.Forbidden:
            pass

    # ── /solved コマンド ────────────────────────────────
    @app_commands.command(name="solved", description="質問が解決したらこのコマンドを実行してください")
    async def solved(self, interaction: discord.Interaction):
        thread = interaction.channel

        # スレッド内でのみ有効
        if not isinstance(thread, discord.Thread):
            await interaction.response.send_message(
                "❌ このコマンドはサポートスレッド内でのみ使用できます。",
                ephemeral=True,
            )
            return

        # サポートフォーラムのスレッドのみ有効
        if thread.parent_id not in config.SUPPORT_FORUM_CHANNEL_IDS:
            await interaction.response.send_message(
                "❌ このコマンドはサポートチャンネルのスレッド内でのみ使用できます。",
                ephemeral=True,
            )
            return

        # スレッドの開始者のみが実行できる
        if thread.owner_id != interaction.user.id:
            await interaction.response.send_message(
                "❌ `/solved` は質問者本人のみ実行できます。",
                ephemeral=True,
            )
            return

        # すでに解決済み
        if discord.utils.get(thread.applied_tags, name="解決済み"):
            await interaction.response.send_message(
                "✅ このスレッドはすでに解決済みです。",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        # 最新の回答者（スレッド開始者以外の最後の投稿者）を探す
        answerer = None
        async for msg in thread.history(limit=50, oldest_first=False):
            if msg.author.id != thread.owner_id and not msg.author.bot:
                answerer = msg.author
                break

        if answerer is None:
            await interaction.followup.send(
                "❌ 回答してくれたメンバーが見つかりません。他のメンバーからの回答がある場合のみ `/solved` を使用してください。",
                ephemeral=True,
            )
            return

        # ポイント加算
        member_data = sheets.add_points(
            discord_id=str(answerer.id),
            username=answerer.display_name,
            delta=config.POINTS_SOLVED,
            action="solved",
            thread_id=str(thread.id),
        )

        # ランクアップチェック
        if member_data:
            points_cog: Points = self.bot.cog.get("Points")
            if points_cog:
                await points_cog._check_rank_up(interaction.guild, answerer, member_data)

        # スレッドに「解決済み」タグを付与してアーカイブ
        try:
            solved_tag = discord.utils.get(thread.parent.available_tags, name="解決済み")
            if solved_tag:
                await thread.edit(
                    applied_tags=thread.applied_tags + [solved_tag],
                    archived=True,
                    reason="/solved コマンドで解決済みに設定",
                )
        except (discord.Forbidden, discord.HTTPException):
            pass

        total = member_data.get("total_points", "？") if member_data else "？"
        await thread.send(
            f"✅ **解決済み！**\n"
            f"{interaction.user.mention} さんが解決済みにしました。\n"
            f"{answerer.mention} さんに **+{config.POINTS_SOLVED} pt** 付与されました！"
            f"（累計: {total} pt）"
        )
        await interaction.followup.send("✅ 解決済みにしました！ありがとうございました。", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Support(bot))
