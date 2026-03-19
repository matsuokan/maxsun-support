"""
cogs/rewards.py - /reward-apply コマンド（報酬申請受付）
"""
from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

import config
from utils import sheets, helpers

# ランクごとの報酬内容
REWARD_INFO: dict[str, dict] = {
    "supporter": {
        "type": "novelty",
        "detail": "MAXSUN ロゴ入りノベルティセット（ステッカー・アクスタ等）",
        "label": "🥈 サポーター特典ノベルティ",
    },
    "expert": {
        "type": "coupon",
        "detail": "MAXSUN 製品 15%OFF クーポン",
        "label": "🥇 エキスパート特典クーポン（15%OFF）",
    },
    "ambassador": {
        "type": "coupon",
        "detail": "MAXSUN 製品 30%OFF クーポン + 限定ノベルティセット",
        "label": "💎 アンバサダー特典クーポン（30%OFF）+ 限定ノベルティセット",
    },
}

ELIGIBLE_RANKS = {"supporter", "expert", "ambassador"}


class RewardApplyModal(discord.ui.Modal, title="報酬申請フォーム"):
    """住所またはメール入力フォーム"""
    shipping_name = discord.ui.TextInput(
        label="氏名（全角）",
        placeholder="例: 山田 太郎",
        required=True,
        max_length=50,
    )
    email = discord.ui.TextInput(
        label="メールアドレス",
        placeholder="例: your@email.com",
        required=True,
        max_length=100,
    )
    shipping_address = discord.ui.TextInput(
        label="送付先住所（ノベルティがある場合のみ）",
        placeholder="例: 東京都渋谷区〇〇1-2-3",
        required=False,
        max_length=200,
        style=discord.TextStyle.paragraph,
    )

    def __init__(self, member_data: dict):
        super().__init__()
        self.member_data = member_data

    async def on_submit(self, interaction: discord.Interaction):
        rank = self.member_data["rank"]
        reward = REWARD_INFO.get(rank)
        if reward is None:
            await interaction.response.send_message(
                "❌ 対象ランクの報酬情報が見つかりませんでした。運営にお問い合わせください。",
                ephemeral=True,
            )
            return

        sheets.append_reward_application(
            discord_id=str(interaction.user.id),
            username=interaction.user.display_name,
            rank=rank,
            reward_type=reward["type"],
            reward_detail=reward["detail"],
            shipping_name=self.shipping_name.value,
            shipping_address=self.shipping_address.value or "",
            email=self.email.value,
        )

        # 運営に通知
        mod_log_ch = interaction.guild.get_channel(config.CHANNEL_MOD_LOG)
        if mod_log_ch:
            await mod_log_ch.send(
                f"📬 **報酬申請** が届きました\n"
                f"ユーザー: {interaction.user.mention}（{rank}）\n"
                f"報酬: {reward['label']}\n"
                f"→ Google Sheets の `rewards_log` を確認してください。"
            )

        await interaction.response.send_message(
            f"✅ **申請を受け付けました！**\n"
            f"報酬: {reward['label']}\n\n"
            f"運営が確認次第、2〜4 週間以内にご連絡します。"
            f"\n個人情報は報酬発送のみに使用します。",
            ephemeral=True,
        )


class Rewards(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="reward-apply", description="報酬（ノベルティ・クーポン）を申請します")
    async def reward_apply(self, interaction: discord.Interaction):
        # 申請チャンネルのみ有効
        if interaction.channel_id != config.CHANNEL_REWARD_APPLY:
            apply_ch = interaction.guild.get_channel(config.CHANNEL_REWARD_APPLY)
            mention = apply_ch.mention if apply_ch else "#受け取り申請"
            await interaction.response.send_message(
                f"❌ このコマンドは {mention} でのみ使用できます。",
                ephemeral=True,
            )
            return

        member_data = sheets.get_member(str(interaction.user.id))
        if member_data is None or member_data["rank"] not in ELIGIBLE_RANKS:
            rank_display = helpers.format_rank_bar(
                member_data["total_points"] if member_data else 0
            )
            await interaction.response.send_message(
                f"❌ 報酬申請には 🥈 **サポーター**（200 pt）以上のランクが必要です。\n{rank_display}",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(RewardApplyModal(member_data))


async def setup(bot: commands.Bot):
    await bot.add_cog(Rewards(bot))
