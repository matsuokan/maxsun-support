"""
cogs/knowledge.py - Discord チャンネルデータの日次収集・ナレッジ蓄積

毎日指定時刻（デフォルト 03:00 JST）にサーバーの全チャンネルから
メッセージ・リアクション・メタデータを収集し、構造化 Markdown として保存する。
"""
from __future__ import annotations

import datetime
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

import discord
import pytz
from discord import app_commands
from discord.ext import commands, tasks

import config

logger = logging.getLogger("maxbot.knowledge")

JST = pytz.timezone("Asia/Tokyo")

# ── 設定 ──────────────────────────────────────────
# 収集時刻（JST）
COLLECT_HOUR = int(os.getenv("KNOWLEDGE_COLLECT_HOUR", "3"))
COLLECT_MINUTE = int(os.getenv("KNOWLEDGE_COLLECT_MINUTE", "0"))

# ナレッジ保存先（デフォルト: リポジトリルート/knowledge/）
KNOWLEDGE_BASE_DIR = Path(os.getenv(
    "KNOWLEDGE_DIR",
    str(Path(__file__).parent.parent.parent / "knowledge")
))

# Git 自動コミット＆プッシュ（明示的に有効化が必要）
GIT_AUTO_PUSH = os.getenv("KNOWLEDGE_GIT_PUSH", "false").lower() == "true"


class KnowledgeCollector(commands.Cog):
    """Discord チャンネルのデータを日次収集し、構造化 Markdown として蓄積する。"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.daily_dir = KNOWLEDGE_BASE_DIR / "daily"

    async def cog_load(self):
        self.collect_task.start()

    async def cog_unload(self):
        self.collect_task.cancel()

    # ── スケジュールタスク ──────────────────────────

    @tasks.loop(
        time=datetime.time(
            hour=COLLECT_HOUR,
            minute=COLLECT_MINUTE,
            tzinfo=JST,
        )
    )
    async def collect_task(self):
        """毎日指定時刻に全チャンネルのデータを収集する。"""
        logger.info("📚 ナレッジ収集を開始します...")
        try:
            stats = await self._collect_all()
            logger.info(
                f"📚 ナレッジ収集完了: "
                f"{stats['channels']} チャンネル, "
                f"{stats['messages']} メッセージ"
            )
        except Exception as e:
            logger.error(f"ナレッジ収集中にエラー: {e}", exc_info=True)

    @collect_task.before_loop
    async def before_collect(self):
        await self.bot.wait_until_ready()

    # ── 管理コマンド ──────────────────────────────

    @app_commands.command(
        name="collect-knowledge",
        description="【管理者】ナレッジ収集を手動で即時実行します",
    )
    @app_commands.checks.has_role(config.ROLE_STAFF)
    async def collect_now(self, interaction: discord.Interaction):
        """ナレッジ収集を手動で実行する（管理者のみ）。"""
        await interaction.response.defer(ephemeral=True)
        stats = await self._collect_all()
        await interaction.followup.send(
            f"✅ ナレッジ収集完了\n"
            f"- チャンネル数: {stats['channels']}\n"
            f"- メッセージ数: {stats['messages']}\n"
            f"- 保存先: `knowledge/daily/{stats['date']}/`",
            ephemeral=True,
        )

    # ── 収集ロジック ────────────────────────────────

    async def _collect_all(self) -> dict:
        """全チャンネルからデータを収集する。"""
        now = datetime.datetime.now(JST)
        since = now - datetime.timedelta(hours=24)
        date_str = now.strftime("%Y-%m-%d")

        stats = {"channels": 0, "messages": 0, "date": date_str}

        for guild in self.bot.guilds:
            output_dir = self.daily_dir / date_str
            output_dir.mkdir(parents=True, exist_ok=True)

            for channel in guild.channels:
                # ボイス / ステージ / カテゴリはスキップ
                if isinstance(channel, (
                    discord.CategoryChannel,
                    discord.VoiceChannel,
                    discord.StageChannel,
                )):
                    continue

                try:
                    result = await self._collect_channel(channel, since, now)
                    if result:
                        content, msg_count = result
                        filepath = output_dir / f"{channel.name}.md"
                        filepath.write_text(content, encoding="utf-8")
                        stats["channels"] += 1
                        stats["messages"] += msg_count
                        logger.info(f"  ✅ #{channel.name} ({msg_count} msgs)")
                except discord.Forbidden:
                    logger.warning(f"  ⛔ #{channel.name} (権限なし)")
                except Exception as e:
                    logger.error(f"  ❌ #{channel.name}: {e}")

            # 収集メタデータ保存
            meta = {
                "collected_at": now.isoformat(),
                "period_start": since.isoformat(),
                "period_end": now.isoformat(),
                "guild": guild.name,
                "guild_id": str(guild.id),
                "stats": stats,
            }
            (output_dir / "_metadata.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        # Git 自動プッシュ
        if GIT_AUTO_PUSH:
            await self._git_push(date_str)

        return stats

    async def _collect_channel(
        self,
        channel: discord.abc.GuildChannel,
        since: datetime.datetime,
        until: datetime.datetime,
    ) -> Optional[tuple[str, int]]:
        """チャンネル種別に応じて収集を振り分ける。"""
        if isinstance(channel, discord.ForumChannel):
            return await self._collect_forum(channel, since, until)
        elif isinstance(channel, discord.TextChannel):
            return await self._collect_text(channel, since, until)
        return None

    # ── テキストチャンネル収集 ───────────────────────

    async def _collect_text(
        self,
        channel: discord.TextChannel,
        since: datetime.datetime,
        until: datetime.datetime,
    ) -> Optional[tuple[str, int]]:
        """テキストチャンネルのメッセージを収集する。"""
        messages = []
        async for msg in channel.history(
            after=since, before=until, limit=1000, oldest_first=True
        ):
            messages.append(msg)

        if not messages:
            return None

        lines = self._frontmatter(
            channel=channel,
            ch_type="text",
            since=since,
            until=until,
            extra={"message_count": len(messages)},
        )

        lines.append(f"# #{channel.name}")
        lines.append("")
        if channel.topic:
            lines.append(f"> {channel.topic}")
            lines.append("")
        lines.append("## メッセージ")
        lines.append("")

        for msg in messages:
            lines.extend(self._format_message(msg))
            lines.append("")

        return "\n".join(lines), len(messages)

    # ── フォーラムチャンネル収集 ──────────────────────

    async def _collect_forum(
        self,
        channel: discord.ForumChannel,
        since: datetime.datetime,
        until: datetime.datetime,
    ) -> Optional[tuple[str, int]]:
        """フォーラムチャンネルのスレッドとメッセージを収集する。"""
        # アクティブスレッド
        threads: list[discord.Thread] = list(channel.threads)

        # アーカイブ済みスレッド（期間内に更新されたもの）
        try:
            async for thread in channel.archived_threads(limit=100):
                if thread.archive_timestamp and thread.archive_timestamp >= since:
                    threads.append(thread)
                else:
                    break  # 古いスレッドはスキップ
        except discord.Forbidden:
            pass

        if not threads:
            return None

        collected_threads: list[tuple[discord.Thread, list[discord.Message]]] = []
        total_messages = 0

        for thread in threads:
            thread_msgs = []
            try:
                async for msg in thread.history(
                    after=since, before=until, limit=500, oldest_first=True
                ):
                    thread_msgs.append(msg)
            except discord.Forbidden:
                continue

            if thread_msgs:
                total_messages += len(thread_msgs)
                collected_threads.append((thread, thread_msgs))

        if not collected_threads:
            return None

        lines = self._frontmatter(
            channel=channel,
            ch_type="forum",
            since=since,
            until=until,
            extra={
                "thread_count": len(collected_threads),
                "total_messages": total_messages,
            },
        )

        lines.append(f"# #{channel.name}")
        lines.append("")
        if channel.topic:
            lines.append(f"> {channel.topic}")
            lines.append("")

        for thread, messages in collected_threads:
            lines.extend(self._format_thread(thread, messages))

        return "\n".join(lines), total_messages

    # ── フォーマッター ─────────────────────────────

    def _frontmatter(
        self,
        channel: discord.abc.GuildChannel,
        ch_type: str,
        since: datetime.datetime,
        until: datetime.datetime,
        extra: dict | None = None,
    ) -> list[str]:
        """YAML フロントマターを生成する。"""
        lines = ["---"]
        lines.append(f'channel: "{channel.name}"')
        lines.append(f'channel_id: "{channel.id}"')
        cat = channel.category.name if channel.category else "なし"
        lines.append(f'category: "{cat}"')
        lines.append(f"type: {ch_type}")

        topic = ""
        if hasattr(channel, "topic") and channel.topic:
            # YAML 内の特殊文字をエスケープ
            topic = channel.topic.replace('"', '\\"').replace("\n", " ")
        lines.append(f'topic: "{topic}"')

        lines.append(f'collected_at: "{until.isoformat()}"')
        lines.append(f'period_start: "{since.isoformat()}"')
        lines.append(f'period_end: "{until.isoformat()}"')

        if extra:
            for k, v in extra.items():
                lines.append(f"{k}: {v}")

        lines.append("---")
        lines.append("")
        return lines

    def _format_thread(
        self, thread: discord.Thread, messages: list[discord.Message]
    ) -> list[str]:
        """フォーラムスレッドを Markdown にフォーマットする。"""
        lines = []
        lines.append(f"## スレッド: {thread.name}")
        lines.append("")
        lines.append("| 項目 | 値 |")
        lines.append("|---|---|")

        owner_name = str(thread.owner) if thread.owner else "不明"
        lines.append(f"| 作成者 | {owner_name} |")

        created = "不明"
        if thread.created_at:
            created = thread.created_at.astimezone(JST).isoformat()
        lines.append(f"| 作成日時 | {created} |")

        lines.append(f"| メッセージ数 | {thread.message_count or len(messages)} |")

        status = "アーカイブ" if thread.archived else "オープン"
        if thread.locked:
            status += "（ロック）"
        lines.append(f"| 状態 | {status} |")

        if hasattr(thread, "applied_tags") and thread.applied_tags:
            tags = ", ".join(t.name for t in thread.applied_tags)
            lines.append(f"| タグ | {tags} |")

        lines.append("")
        lines.append("### メッセージ")
        lines.append("")

        for msg in messages:
            lines.extend(self._format_message(msg))
            lines.append("")

        lines.append("---")
        lines.append("")
        return lines

    def _format_message(self, msg: discord.Message) -> list[str]:
        """1つのメッセージを Markdown 行のリストに変換する。"""
        lines = []

        # ── ヘッダー: 著者 — タイムスタンプ
        timestamp = msg.created_at.astimezone(JST).strftime(
            "%Y-%m-%dT%H:%M:%S+09:00"
        )
        author_name = msg.author.display_name if msg.author else "不明"
        author_id = str(msg.author.id) if msg.author else "0"
        is_bot = msg.author.bot if msg.author else False
        bot_tag = " `[BOT]`" if is_bot else ""

        lines.append(f"**{author_name}** (ID: {author_id}){bot_tag} — {timestamp}")
        lines.append("")

        # ── 返信先
        if msg.reference and msg.reference.message_id:
            lines.append(f"> ↩️ 返信先: Message ID {msg.reference.message_id}")
            lines.append("")

        # ── 本文
        content = msg.content
        if not content and msg.embeds:
            embed_parts = []
            for embed in msg.embeds:
                if embed.title:
                    embed_parts.append(f"**{embed.title}**")
                if embed.description:
                    embed_parts.append(embed.description)
                for field in embed.fields:
                    embed_parts.append(f"- **{field.name}**: {field.value}")
            content = "\n".join(embed_parts) if embed_parts else "[Embed]"
        elif not content:
            content = "[コンテンツなし]"

        for line in content.split("\n"):
            lines.append(line)
        lines.append("")

        # ── 添付ファイル
        if msg.attachments:
            lines.append("📎 **添付ファイル:**")
            for att in msg.attachments:
                size_kb = att.size / 1024
                lines.append(f"- [{att.filename}]({att.url}) ({size_kb:.1f} KB)")
            lines.append("")

        # ── リアクション
        if msg.reactions:
            reaction_parts = []
            for reaction in msg.reactions:
                reaction_parts.append(f"{reaction.emoji} ×{reaction.count}")
            lines.append(f"**リアクション:** {' | '.join(reaction_parts)}")
        else:
            lines.append("**リアクション:** なし")

        return lines

    # ── Git 操作 ────────────────────────────────

    async def _git_push(self, date_str: str):
        """knowledge/ の変更を Git コミット＆プッシュする。"""
        repo_root = KNOWLEDGE_BASE_DIR.parent
        try:
            subprocess.run(
                ["git", "add", "knowledge/"],
                cwd=repo_root, check=True, capture_output=True,
            )
            result = subprocess.run(
                ["git", "status", "--porcelain", "knowledge/"],
                cwd=repo_root, check=True, capture_output=True, text=True,
            )
            if not result.stdout.strip():
                logger.info("Git: ナレッジに変更なし")
                return

            subprocess.run(
                ["git", "commit", "-m",
                 f"knowledge: daily collection {date_str}"],
                cwd=repo_root, check=True, capture_output=True,
            )
            subprocess.run(
                ["git", "push"],
                cwd=repo_root, check=True, capture_output=True,
            )
            logger.info(f"Git: ナレッジをプッシュしました ({date_str})")
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Git 操作エラー: {e.stderr.decode() if e.stderr else e}"
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(KnowledgeCollector(bot))
