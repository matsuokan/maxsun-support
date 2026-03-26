"""#discord-使い方ガイド にコンテンツを投稿"""
import asyncio, os, sys
import discord
from dotenv import load_dotenv
load_dotenv()

MESSAGES = [
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
    "• 画像はドラッグ＆ドロップ or 📎 ボタンで添付",

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
]

async def main():
    client = discord.Client(intents=discord.Intents.default())

    @client.event
    async def on_ready():
        print(f"接続: {client.user}", flush=True)
        guild = client.guilds[0]
        ch = discord.utils.get(guild.text_channels, name="discord-使い方ガイド")
        if not ch:
            print("❌ チャンネルが見つかりません", flush=True)
            await client.close()
            return
        print(f"投稿先: #{ch.name}", flush=True)
        for i, msg in enumerate(MESSAGES, 1):
            await ch.send(msg)
            print(f"✅ {i}/{len(MESSAGES)} 投稿", flush=True)
        print("🎉 完了！", flush=True)
        await client.close()

    await client.start(os.environ["DISCORD_TOKEN"])

asyncio.run(main())
