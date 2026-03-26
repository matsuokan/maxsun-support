"""
cogs/setup.py - チャンネルコンテンツの自動投稿（運営専用）
"""
from __future__ import annotations

import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

import config

logger = logging.getLogger("maxbot.setup")


def is_staff():
    async def predicate(interaction: discord.Interaction) -> bool:
        # ROLE_STAFF が未設定（0）の場合は権限チェックをスキップ（テスト用）
        if config.ROLE_STAFF == 0:
            return True
        staff_role = interaction.guild.get_role(config.ROLE_STAFF)
        user_role_ids = [r.id for r in interaction.user.roles]
        logger.info(
            f"[is_staff] user={interaction.user.name}, "
            f"ROLE_STAFF={config.ROLE_STAFF}, "
            f"staff_role_found={staff_role is not None}, "
            f"user_roles={user_role_ids}"
        )
        if staff_role and staff_role in interaction.user.roles:
            return True
        await interaction.response.send_message(
            "❌ このコマンドは運営のみ使用できます。", ephemeral=True
        )
        return False
    return app_commands.check(predicate)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# チャンネル名 → 投稿メッセージリスト
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHANNEL_CONTENT: dict[str, list[str]] = {
    # ── 📢 お知らせ ──
    "お知らせ": [
        "📢 **MAXSUN コミュニティサポートへようこそ！**\n\n"
        "このチャンネルでは、MAXSUN から以下の情報をお届けします：\n\n"
        "🔹 製品アップデート情報\n"
        "🔹 イベント・キャンペーンのお知らせ\n"
        "🔹 ポイント制度・報酬に関する変更\n"
        "🔹 コミュニティに関する重要なお知らせ\n\n"
        "> ※ このチャンネルは運営からの発信専用です。質問やコメントは #雑談 でお気軽にどうぞ！",
    ],

    "新製品情報": [
        "🆕 **新製品・アップデート情報チャンネル**\n\n"
        "MAXSUN の最新情報をいち早くお届けします：\n\n"
        "🔸 新製品の発売情報\n"
        "🔸 BIOS アップデートのリリースノート\n"
        "🔸 ドライバの更新情報\n"
        "🔸 製品仕様の変更・改善情報\n\n"
        "> ※ 製品に関するご質問は「❓テクニカルサポート」カテゴリの各チャンネルへどうぞ。",
    ],

    # ── 🆕 はじめに ──
    "はじめにお読みください": [
        # メッセージ①：ようこそ
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎉 MAXSUN コミュニティサポートへようこそ！\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "このサーバーは、MAXSUN 製品（マザーボード・グラフィックボード）を使うユーザー同士が助け合うコミュニティです。\n\n"
        "💡 **このサーバーでできること**\n"
        "• 製品の使い方やトラブルについて質問・回答\n"
        "• 他のユーザーの質問に回答してポイントを獲得\n"
        "• ポイントを貯めてノベルティや製品割引クーポンをゲット\n"
        "• 自作 PC の情報交換・ベンチマーク共有\n\n"
        "📌 **まずこのチャンネルの内容をすべてお読みください。**\n"
        "ルールを確認したら、下の ✅ リアクションを押して参加しましょう！",

        # メッセージ②：基本ルール
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📜 コミュニティルール\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "このサーバーでは、すべてのメンバーが快適に参加できるよう以下のルールを設けています。\n\n"
        "**1️⃣ 相互尊重**\n"
        "すべてのメンバーに敬意を持って接してください。個人攻撃・侮辱・差別的発言は禁止です。\n\n"
        "**2️⃣ 正確な情報を**\n"
        "技術的な回答は、確認済みの情報を投稿してください。不確かな場合は「〜だと思います」と明記をお願いします。\n\n"
        "**3️⃣ チャンネルの正しい使い方**\n"
        "各チャンネルの用途に沿った投稿をしてください。質問は製品カテゴリに合ったサポートチャンネルへ。\n\n"
        "**4️⃣ 解決したら /solved**\n"
        "質問が解決したら、必ず `/solved` コマンドを実行してください。回答者にポイントが付与されます。\n\n"
        "**5️⃣ 禁止事項**\n"
        "🚫 スパム・荒らし行為\n"
        "🚫 個人情報の無断掲載\n"
        "🚫 違法コンテンツの共有\n"
        "🚫 競合他社製品の中傷\n"
        "🚫 無関係な宣伝・広告",

        # メッセージ③：ポイント制度
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⭐ ポイント制度のご案内\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "このサーバーでは、コミュニティへの貢献に応じて**ポイント**が貯まります！\n\n"
        "📊 **ポイントの貯め方**\n"
        "• 質問者が `/solved` で解決マーク → 回答者に **+20 pt**\n"
        "• あなたの回答に 👍 リアクション → **+1 pt**（リアクションごと）\n"
        "• 運営からの特別ボーナス → **任意 pt**",

        # メッセージ④：ランク表
        "🏅 **ランクと特典**\n\n"
        "🥉 **ヘルパー**（0〜199 pt）\n"
        "→ コミュニティ参加・投稿権限\n\n"
        "🥈 **サポーター**（200〜999 pt）\n"
        "→ 専用バッジ + MAXSUN ノベルティグッズ申請権\n\n"
        "🥇 **エキスパート**（1,000〜4,999 pt）\n"
        "→ 専用バッジ + 製品割引クーポン（10〜20%OFF）申請権\n\n"
        "💎 **アンバサダー**（5,000 pt〜）\n"
        "→ 専用バッジ + 上位クーポン（30%OFF）+ 限定ノベルティセット申請権\n\n"
        "⚠️ ポイントに関する注意\n"
        "• 自分の質問に自分で `/solved` は使えません\n"
        "• 複数アカウントによるポイント操作は Ban 対象です\n"
        "• 意図的な誤情報の提供は −10 pt のペナルティです",

        # メッセージ⑤：使い方ガイド
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🗺️ サーバーの使い方ガイド\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**🔹 質問したいとき**\n"
        "1. 「❓テクニカルサポート」カテゴリから合うチャンネルを選ぶ\n"
        "2. 新しいスレッドを立てる\n"
        "3. テンプレートに沿って製品名・症状を記入\n"
        "4. 解決したら `/solved` を実行！\n\n"
        "**🔹 回答したいとき**\n"
        "1. サポートチャンネルの未解決スレッドを見る\n"
        "2. 知識のあるスレッドに回答を投稿\n"
        "3. 質問者が `/solved` すると +20 pt！\n\n"
        "**🔹 よく使うコマンド**\n"
        "• `/mypoints` — 自分のポイント・ランクを確認\n"
        "• `/leaderboard` — ポイント上位10名を表示\n"
        "• `/solved` — 質問を解決済みにする\n"
        "• `/reward-apply` — 報酬を申請する\n"
        "• `/faq キーワード` — FAQ を検索\n\n"
        "**✅ ルールを読んだら、このメッセージに ✅ リアクションを押してください！**\n"
        "🥉 ヘルパー ロールが付与され、サーバーの全機能が使えるようになります。",
    ],

    "discord-使い方ガイド": [
        # メッセージ①：基本操作
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📖 Discord の使い方ガイド\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Discord が初めての方向けに、基本操作をまとめました。\n"
        "わからないことがあれば #雑談 でお気軽に聞いてください！\n\n"
        "📌 **サーバーの構造**\n"
        "• **カテゴリ**（📢 お知らせ、❓ テクニカルサポート 等）= チャンネルのグループ\n"
        "• **チャンネル**（# マーク）= 話題ごとの部屋\n"
        "• **スレッド** = チャンネルの中の個別トピック（質問ごとの小部屋）\n\n"
        "📌 **メッセージの送り方**\n"
        "• 画面下の入力欄にテキストを入力して Enter で送信\n"
        "• Shift + Enter で改行（送信せずに改行）\n"
        "• 画像はドラッグ＆ドロップ or ＋ ボタンから「ファイルをアップロード」で添付",

        # メッセージ②：質問の仕方
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "❓ テクニカルサポートでの質問方法\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "サポートチャンネル（#マザーボード-サポート 等）は**フォーラム形式**です。\n"
        "掲示板のように、質問ごとにスレッドを作って投稿します。\n\n"
        "📝 **質問の手順**\n"
        "1. 左のチャンネル一覧から、質問に合うサポートチャンネルをクリック\n"
        "2. 画面上部の「**投稿を作成**」ボタンをクリック\n"
        "3. **タイトル**に質問の概要を入力（例:「BIOSが起動しない」）\n"
        "4. **本文**に詳細を記入（製品名・症状・試したこと）\n"
        "5. 「投稿」ボタンで送信！\n\n"
        "📝 **解決したら**\n"
        "質問が解決したら、スレッド内で `/solved` と入力して送信してください。\n"
        "回答してくれた方にポイントが付与されます ✅\n\n"
        "> 📱 スマホの場合は右下の ＋ ボタンからスレッドを作成できます。",

        # メッセージ③：便利な機能
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 知っておくと便利な機能\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔹 **リアクション（👍 等）**\n"
        "メッセージにカーソルを合わせると顔文字アイコンが出ます。\n"
        "クリックしてリアクションを選べます。\n"
        "役に立った回答に 👍 を付けると、回答者にポイント +1 pt！\n\n"
        "🔹 **メンション（@ユーザー名）**\n"
        "特定の人に話しかけたいときは @ を付けて名前を入力。\n"
        "相手に通知が届きます。\n\n"
        "🔹 **スラッシュコマンド**\n"
        "入力欄に `/` を打つと、使えるコマンド一覧が表示されます。\n"
        "• `/mypoints` → 自分のポイントを確認\n"
        "• `/leaderboard` → ランキングを見る\n\n"
        "🔹 **ピン留めメッセージ**\n"
        "チャンネル上部の 📌 アイコンから、重要なメッセージを確認できます。\n\n"
        "📖 Discord 公式ヘルプ: https://support.discord.com/hc/ja",
    ],

    # ── ❓ テクニカルサポート（フォーラム） ──
    # フォーラムチャンネルにはガイドラインメッセージとして投稿
    "マザーボード-サポート": [
        "📋 **マザーボードサポートへようこそ**\n\n"
        "MAXSUN マザーボードに関する質問はこちらへ。\n\n"
        "📝 スレッドを立てるときは以下を記載してください：\n"
        "• 製品名・型番（例: MS-B760M POWER）\n"
        "• OS・バージョン\n"
        "• 症状・エラー内容\n"
        "• 試したこと\n\n"
        "✅ 解決したら `/solved` コマンドを実行してください。回答者にポイントが付与されます。",
    ],

    "グラフィックボード-サポート": [
        "📋 **グラフィックボードサポートへようこそ**\n\n"
        "MAXSUN グラフィックボードに関する質問はこちらへ。\n\n"
        "📝 スレッドを立てるときは以下を記載してください：\n"
        "• 製品名・型番（例: MS-RX7900XT GAMING X 24G）\n"
        "• OS・バージョン、ドライババージョン\n"
        "• 症状・エラー内容\n"
        "• 試したこと\n\n"
        "✅ 解決したら `/solved` コマンドを実行してください。回答者にポイントが付与されます。",
    ],

    "bios-ドライバ": [
        "📋 **BIOS・ドライバサポートへようこそ**\n\n"
        "BIOS やドライバに関する質問はこちらへ。\n\n"
        "📝 スレッドを立てるときは以下を記載してください：\n"
        "• 製品名・型番\n"
        "• 現在の BIOS / ドライババージョン\n"
        "• やりたいこと or 症状\n"
        "• 試したこと\n\n"
        "⚠️ BIOS アップデートは慎重に行ってください。不明点はスレッドで確認してから実行しましょう。\n"
        "✅ 解決したら `/solved` コマンドを実行してください。",
    ],

    "互換性-構成相談": [
        "📋 **互換性・構成相談へようこそ**\n\n"
        "MAXSUN 製品と他パーツの互換性や、PC 構成の相談はこちらへ。\n\n"
        "📝 スレッドを立てるときは以下を記載してください：\n"
        "• 検討中の MAXSUN 製品（型番）\n"
        "• 組み合わせたいパーツ（CPU・メモリ・電源等）\n"
        "• 用途（ゲーム・作業・サーバー等）\n"
        "• 予算（任意）\n\n"
        "💡 購入前の相談も大歓迎です！\n"
        "✅ 解決したら `/solved` コマンドを実行してください。",
    ],

    "解決済みアーカイブ": [
        "📚 **解決済みアーカイブ**\n\n"
        "サポートチャンネルで解決した質問のうち、特に参考になるものをこちらにまとめています。\n\n"
        "質問する前にこちらを確認すると、同じ問題の解決策が見つかるかもしれません。\n\n"
        "> 💡 キーワードで FAQ を検索したい場合は `/faq キーワード` コマンドも使えます。\n"
        "> ※ このチャンネルは読み取り専用です。",
    ],

    # ── 💬 コミュニティ ──
    "自作pc-作例紹介": [
        "🖥️ **自作 PC 作例紹介チャンネル**\n\n"
        "あなたの自作 PC を見せてください！\n"
        "MAXSUN パーツを使ったビルドの写真やスペックをシェアしましょう 🎉\n\n"
        "📸 **投稿フォーマット（任意）**\n"
        "• 構成（CPU / マザーボード / GPU / メモリ等）\n"
        "• MAXSUN 製品：（型番）\n"
        "• こだわりポイント\n"
        "• 写真\n\n"
        "> 他のメンバーの投稿に 👍 リアクションで応援しましょう！",
    ],

    "ベンチマーク-報告": [
        "📊 **ベンチマーク報告チャンネル**\n\n"
        "MAXSUN 製品のベンチマーク結果やパフォーマンス比較をシェアしましょう！\n\n"
        "📝 **投稿フォーマット（推奨）**\n"
        "• 製品名（型番）\n"
        "• テスト環境（CPU / メモリ / OS 等）\n"
        "• ベンチマークツール（3DMark / Cinebench / CrystalDiskMark 等）\n"
        "• スコア・結果\n"
        "• スクリーンショット（あれば）\n\n"
        "> 購入検討中の方の参考になります 💡",
    ],

    "要望-フィードバック": [
        "💡 **要望・フィードバックチャンネル**\n\n"
        "MAXSUN 製品やこのコミュニティに対する要望・改善提案をお聞かせください。\n\n"
        "📝 **投稿のポイント**\n"
        "• 具体的な内容（どの製品の何を改善してほしいか）\n"
        "• 理由や背景\n"
        "• 代替案があれば\n\n"
        "いただいたフィードバックは運営チームが確認し、対応を検討します。\n\n"
        "> ⚠ 緊急の不具合報告は「❓テクニカルサポート」カテゴリへお願いします。",
    ],

    # ── 🏆 ランキング・報酬 ──
    "ポイントランキング": [
        "🏆 **ポイントランキングチャンネル**\n\n"
        "このチャンネルには Bot が自動で以下を投稿します：\n\n"
        "📅 **毎週日曜 0:00** — 週間 & 累計ポイント上位10名のランキング\n"
        "🎉 **ランクアップ時** — メンバーの昇格通知\n\n"
        "> 自分のポイントは `/mypoints` コマンドでいつでも確認できます！",
    ],

    "報酬情報": [
        "🎁 **報酬情報**\n\n"
        "ポイントを貯めてランクが上がると、以下の特典を申請できます！\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🥈 **サポーター**（200 pt〜）\n"
        "🎁 MAXSUN ロゴ入りノベルティ（ステッカー・アクリルスタンド等）\n\n"
        "🥇 **エキスパート**（1,000 pt〜）\n"
        "🎫 製品割引クーポン（10〜20% OFF）\n\n"
        "💎 **アンバサダー**（5,000 pt〜）\n"
        "🎫 上位クーポン（30% OFF）\n"
        "🎁 限定ノベルティセット\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 **申請方法**\n"
        "1. `/mypoints` で自分のランクを確認\n"
        "2. #受け取り申請 チャンネルで `/reward-apply` を実行\n"
        "3. フォームに必要情報を入力して送信\n"
        "4. 運営が確認後、2〜4 週間でお届け\n\n"
        "⚠️ **注意事項**\n"
        "• 申請はランク到達後 3ヶ月以内に行ってください\n"
        "• 報酬の換金・転売・譲渡は禁止です\n"
        "• 不正取得が判明した場合は報酬無効 + アカウント停止対象です",
    ],

    "受け取り申請": [
        "📦 **報酬の受け取り申請**\n\n"
        "ランク特典の申請はこのチャンネルで行ってください。\n\n"
        "**申請手順**\n"
        "1. `/reward-apply` コマンドを入力\n"
        "2. 表示されるフォームに必要情報を記入\n"
        "3. 送信後、運営が内容を確認します\n"
        "4. 確認完了後、2〜4 週間でお届けします\n\n"
        "> 💡 報酬の詳細は #報酬情報 をご確認ください。\n"
        "> 📊 自分のランクは `/mypoints` で確認できます。",
    ],
}


def _find_channel(guild: discord.Guild, name: str) -> Optional[discord.abc.GuildChannel]:
    """チャンネル名（部分一致）でチャンネルを検索する"""
    # 完全一致を優先
    for ch in guild.channels:
        if ch.name == name:
            return ch
    # 部分一致（ハイフンの有無など吸収）
    normalized = name.replace("-", "").replace("_", "").replace(" ", "")
    for ch in guild.channels:
        ch_normalized = ch.name.replace("-", "").replace("_", "").replace(" ", "")
        if ch_normalized == normalized:
            return ch
    return None


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="setup-channels",
        description="【運営】全チャンネルにコンテンツを一括投稿します",
    )
    @is_staff()
    async def setup_channels(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        results: list[str] = []
        success = 0
        failed = 0

        for channel_name, messages in CHANNEL_CONTENT.items():
            ch = _find_channel(guild, channel_name)
            if ch is None:
                results.append(f"❌ `{channel_name}` — チャンネルが見つかりません")
                failed += 1
                continue

            try:
                # フォーラムチャンネルの場合はスレッドではなく通常テキストとして投稿を試みる
                if isinstance(ch, discord.ForumChannel):
                    # フォーラムにはガイドラインスレッドを作成
                    thread, _msg = await ch.create_thread(
                        name="📋 ガイドライン",
                        content=messages[0],
                    )
                    for msg in messages[1:]:
                        await thread.send(msg)
                    results.append(f"✅ `{channel_name}` — ガイドラインスレッドを作成")
                else:
                    # テキストチャンネルにメッセージを順番に投稿
                    for msg in messages:
                        await ch.send(msg)
                    results.append(f"✅ `{channel_name}` — {len(messages)} 件投稿")
                success += 1
            except discord.Forbidden:
                results.append(f"⛔ `{channel_name}` — 権限がありません")
                failed += 1
            except Exception as e:
                results.append(f"❌ `{channel_name}` — エラー: {e}")
                failed += 1

        summary = f"**セットアップ完了**\n✅ 成功: {success}　❌ 失敗: {failed}\n\n"
        summary += "\n".join(results)

        # Discord のメッセージ上限（2000文字）を考慮して分割
        if len(summary) > 2000:
            await interaction.followup.send(summary[:2000], ephemeral=True)
            await interaction.followup.send(summary[2000:], ephemeral=True)
        else:
            await interaction.followup.send(summary, ephemeral=True)

    @app_commands.command(
        name="setup-channel",
        description="【運営】指定チャンネルにコンテンツを投稿します",
    )
    @app_commands.describe(channel_name="投稿先チャンネル名（例: お知らせ）")
    @is_staff()
    async def setup_channel(
        self, interaction: discord.Interaction, channel_name: str
    ):
        await interaction.response.defer(ephemeral=True)

        if channel_name not in CHANNEL_CONTENT:
            available = ", ".join(f"`{k}`" for k in CHANNEL_CONTENT.keys())
            await interaction.followup.send(
                f"❌ `{channel_name}` は登録されていません。\n\n利用可能なチャンネル名:\n{available}",
                ephemeral=True,
            )
            return

        ch = _find_channel(interaction.guild, channel_name)
        if ch is None:
            await interaction.followup.send(
                f"❌ サーバー内に `{channel_name}` チャンネルが見つかりません。",
                ephemeral=True,
            )
            return

        messages = CHANNEL_CONTENT[channel_name]
        try:
            if isinstance(ch, discord.ForumChannel):
                thread, _msg = await ch.create_thread(
                    name="📋 ガイドライン",
                    content=messages[0],
                )
                for msg in messages[1:]:
                    await thread.send(msg)
                await interaction.followup.send(
                    f"✅ `{channel_name}` にガイドラインスレッドを作成しました。",
                    ephemeral=True,
                )
            else:
                for msg in messages:
                    await ch.send(msg)
                await interaction.followup.send(
                    f"✅ `{channel_name}` に {len(messages)} 件のメッセージを投稿しました。",
                    ephemeral=True,
                )
        except discord.Forbidden:
            await interaction.followup.send(
                f"⛔ `{channel_name}` への投稿権限がありません。Bot の権限を確認してください。",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ `{channel_name}` への投稿でエラーが発生しました: {e}",
                ephemeral=True,
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
