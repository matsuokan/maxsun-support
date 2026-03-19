"""
cogs/points.py - ポイント加算・リアクション検知
"""
from __future__ import annotations

import discord
from discord.ext import commands

import config
from utils import sheets, helpers


class Points(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── 👍 リアクション追加イベント ────────────────────────
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # 👍 以外は無視
        if str(payload.emoji) != "👍":
            return
        # Bot 自身のリアクションは無視
        if payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        channel = guild.get_channel(payload.channel_id)

        # サポート系チャンネル（またはそのスレッド）のみカウント
        parent_id = getattr(channel, "parent_id", None) or payload.channel_id
        if parent_id not in config.SUPPORT_FORUM_CHANNEL_IDS:
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return

        # 自分のメッセージへの自分のリアクションは無効
        if message.author.id == payload.user_id:
            return

        target_user = message.author
        member_data = sheets.add_points(
            discord_id=str(target_user.id),
            username=target_user.display_name,
            delta=config.POINTS_REACTION,
            action="reaction_received",
            thread_id=str(payload.message_id),
        )
        if member_data:
            await self._check_rank_up(guild, target_user, member_data)

    # ── 内部: ランクアップチェック ────────────────────────
    async def _check_rank_up(
        self,
        guild: discord.Guild,
        user: discord.Member | discord.User,
        member_data: dict,
    ):
        """ポイント変動後のランクアップをチェックして処理する。"""
        new_rank = helpers.get_rank_from_points(member_data["total_points"])
        current_rank = member_data.get("rank", "helper")
        if new_rank == current_rank:
            return

        rank_order = ["helper", "supporter", "expert", "ambassador"]
        if rank_order.index(new_rank) <= rank_order.index(current_rank):
            return

        # ランク更新
        sheets.update_rank(str(user.id), new_rank)

        # Discord ロール付与
        member = guild.get_member(user.id)
        if member:
            old_role = guild.get_role(config.RANK_ROLE_MAP.get(current_rank))
            new_role = guild.get_role(config.RANK_ROLE_MAP.get(new_rank))
            if old_role:
                await member.remove_roles(old_role, reason="ランクアップ")
            if new_role:
                await member.add_roles(new_role, reason="ランクアップ")

        # ランキングチャンネルに通知
        ranking_ch = guild.get_channel(config.CHANNEL_RANKING)
        if ranking_ch:
            rank_display = helpers.rank_emoji(new_rank)
            reward_hint = ""
            if new_rank in ("supporter", "expert", "ambassador"):
                reward_hint = f"\n`/reward-apply` コマンドで報酬を申請できます 🎁"
            await ranking_ch.send(
                f"🎉 {member.mention if member else user.display_name} さんがランクアップしました！\n"
                f"{rank_display} 達成（{member_data['total_points']} pt）{reward_hint}"
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Points(bot))
