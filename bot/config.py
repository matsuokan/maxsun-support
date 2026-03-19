"""
config.py - 環境変数と設定値の読み込み
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Discord ──────────────────────────────────────
DISCORD_TOKEN: str = os.environ["DISCORD_TOKEN"]

# ── Google Sheets ─────────────────────────────────
GOOGLE_SHEETS_ID: str = os.environ["GOOGLE_SHEETS_ID"]
GOOGLE_SERVICE_ACCOUNT_JSON: str = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_JSON", "./credentials.json"
)

# ── チャンネル ID ─────────────────────────────────
CHANNEL_RANKING: int = int(os.environ["CHANNEL_RANKING"])
CHANNEL_REWARD_APPLY: int = int(os.environ["CHANNEL_REWARD_APPLY"])
CHANNEL_MOD_LOG: int = int(os.environ["CHANNEL_MOD_LOG"])

# サポートフォーラムチャンネル ID リスト（カンマ区切りで複数指定可）
_support_ids = os.getenv("SUPPORT_FORUM_CHANNEL_IDS", "")
SUPPORT_FORUM_CHANNEL_IDS: list[int] = [
    int(x.strip()) for x in _support_ids.split(",") if x.strip()
]

# ── ロール ID ─────────────────────────────────────
ROLE_HELPER: int = int(os.environ["ROLE_HELPER"])
ROLE_SUPPORTER: int = int(os.environ["ROLE_SUPPORTER"])
ROLE_EXPERT: int = int(os.environ["ROLE_EXPERT"])
ROLE_AMBASSADOR: int = int(os.environ["ROLE_AMBASSADOR"])
ROLE_STAFF: int = int(os.environ["ROLE_STAFF"])

# ── ポイントルール（config シートで上書き可能、初期値）─────
POINTS_SOLVED: int = 20
POINTS_REACTION: int = 1
RANK_THRESHOLDS: dict[str, int] = {
    "supporter": 200,
    "expert": 1000,
    "ambassador": 5000,
}

# ランク名 → ロール ID のマッピング
RANK_ROLE_MAP: dict[str, int] = {
    "helper": ROLE_HELPER,
    "supporter": ROLE_SUPPORTER,
    "expert": ROLE_EXPERT,
    "ambassador": ROLE_AMBASSADOR,
}

# ランク表示名
RANK_DISPLAY: dict[str, str] = {
    "helper": "🥉 ヘルパー",
    "supporter": "🥈 サポーター",
    "expert": "🥇 エキスパート",
    "ambassador": "💎 アンバサダー",
}

# ── スケジューラー設定 ────────────────────────────
TIMEZONE: str = "Asia/Tokyo"
WEEKLY_RESET_DAY: str = "monday"   # 週次ポイントリセット曜日
RANKING_POST_DAY: str = "sunday"   # ランキング投稿曜日
RANKING_POST_HOUR: int = 0         # ランキング投稿時刻（時）
RANKING_POST_MINUTE: int = 0       # ランキング投稿時刻（分）
