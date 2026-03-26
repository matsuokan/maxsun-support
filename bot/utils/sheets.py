"""
utils/sheets.py - Google Sheets API ラッパー
"""
from __future__ import annotations

import datetime
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials

import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

_client: Optional[gspread.Client] = None
_spreadsheet: Optional[gspread.Spreadsheet] = None


def _get_spreadsheet() -> gspread.Spreadsheet:
    """スプレッドシートへの接続を返す（シングルトン）"""
    global _client, _spreadsheet
    if _spreadsheet is None:
        if not config.SHEETS_ENABLED:
            raise RuntimeError(
                "Google Sheets が設定されていません。"
                ".env に GOOGLE_SHEETS_ID を設定してください。"
            )
        creds = Credentials.from_service_account_file(
            config.GOOGLE_SERVICE_ACCOUNT_JSON, scopes=SCOPES
        )
        _client = gspread.authorize(creds)
        _spreadsheet = _client.open_by_key(config.GOOGLE_SHEETS_ID)
    return _spreadsheet


def _sheet(name: str) -> gspread.Worksheet:
    return _get_spreadsheet().worksheet(name)


# ──────────────────────────────────────────────────
# members シート操作
# ──────────────────────────────────────────────────

def get_member(discord_id: str) -> Optional[dict]:
    """discord_id でメンバー行を取得。存在しなければ None を返す。"""
    ws = _sheet("members")
    records = ws.get_all_records()
    for r in records:
        if str(r["discord_id"]) == str(discord_id):
            return r
    return None


def upsert_member(discord_id: str, username: str) -> dict:
    """メンバーが存在しなければ作成、存在すれば username を更新して返す。"""
    ws = _sheet("members")
    now = _now()
    member = get_member(discord_id)
    if member is None:
        new_row = [
            discord_id, username, 0, 0, "helper", 0, 0, now, now
        ]
        ws.append_row(new_row, value_input_option="USER_ENTERED")
        return {
            "discord_id": discord_id,
            "username": username,
            "total_points": 0,
            "weekly_points": 0,
            "rank": "helper",
            "solved_count": 0,
            "reaction_count": 0,
        }
    # username が変わっていれば更新
    records = ws.get_all_records()
    for i, r in enumerate(records, start=2):
        if str(r["discord_id"]) == str(discord_id):
            if r["username"] != username:
                ws.update_cell(i, 2, username)
            ws.update_cell(i, 9, now)  # updated_at
            break
    return member


def add_points(
    discord_id: str,
    username: str,
    delta: int,
    action: str,
    thread_id: Optional[str] = None,
    note: str = "",
) -> dict:
    """
    ポイントを加減算し、更新後のメンバー情報を返す。
    point_log にも記録する。
    """
    upsert_member(discord_id, username)
    ws = _sheet("members")
    records = ws.get_all_records()
    now = _now()

    for i, r in enumerate(records, start=2):
        if str(r["discord_id"]) == str(discord_id):
            new_total = int(r["total_points"]) + delta
            new_weekly = int(r["weekly_points"]) + delta
            # solved / reaction_count も更新
            new_solved = int(r["solved_count"]) + (1 if action == "solved" else 0)
            new_reaction = int(r["reaction_count"]) + (
                1 if action == "reaction_received" else 0
            )
            ws.update(
                f"C{i}:I{i}",
                [[new_total, new_weekly, r["rank"], new_solved, new_reaction, r["joined_at"], now]],
                value_input_option="USER_ENTERED",
            )
            updated = dict(r)
            updated["total_points"] = new_total
            updated["weekly_points"] = new_weekly
            updated["solved_count"] = new_solved
            updated["reaction_count"] = new_reaction
            # point_log に追記
            _append_point_log(
                discord_id=discord_id,
                username=username,
                action=action,
                delta=delta,
                total_after=new_total,
                thread_id=thread_id,
                note=note,
            )
            return updated
    return {}


def update_rank(discord_id: str, new_rank: str) -> None:
    """members シートのランクを更新する。"""
    ws = _sheet("members")
    records = ws.get_all_records()
    for i, r in enumerate(records, start=2):
        if str(r["discord_id"]) == str(discord_id):
            ws.update_cell(i, 5, new_rank)
            ws.update_cell(i, 9, _now())
            break


def get_leaderboard(limit: int = 10) -> list[dict]:
    """累計ポイント上位 limit 件を返す。"""
    ws = _sheet("members")
    records = ws.get_all_records()
    sorted_records = sorted(records, key=lambda r: int(r["total_points"]), reverse=True)
    return sorted_records[:limit]


def get_weekly_leaderboard(limit: int = 10) -> list[dict]:
    """週間ポイント上位 limit 件を返す。"""
    ws = _sheet("members")
    records = ws.get_all_records()
    sorted_records = sorted(records, key=lambda r: int(r["weekly_points"]), reverse=True)
    return sorted_records[:limit]


def reset_weekly_points() -> None:
    """全メンバーの weekly_points を 0 にリセットする。"""
    ws = _sheet("members")
    records = ws.get_all_records()
    for i, _ in enumerate(records, start=2):
        ws.update_cell(i, 4, 0)


# ──────────────────────────────────────────────────
# rewards_log シート操作
# ──────────────────────────────────────────────────

def append_reward_application(
    discord_id: str,
    username: str,
    rank: str,
    reward_type: str,
    reward_detail: str,
    shipping_name: str,
    shipping_address: str,
    email: str,
) -> None:
    """報酬申請を rewards_log に記録する。"""
    ws = _sheet("rewards_log")
    ws.append_row(
        [
            _now(), discord_id, username, rank,
            reward_type, reward_detail,
            shipping_name, shipping_address, email,
            "pending", "", "", "",
        ],
        value_input_option="USER_ENTERED",
    )


# ──────────────────────────────────────────────────
# faq シート操作
# ──────────────────────────────────────────────────

def search_faq(keyword: str) -> list[dict]:
    """キーワードで FAQ を検索して最大5件返す。"""
    ws = _sheet("faq")
    records = ws.get_all_records()
    keyword_lower = keyword.lower()
    results = []
    for r in records:
        if not r.get("is_active", True):
            continue
        if (
            keyword_lower in str(r.get("keywords", "")).lower()
            or keyword_lower in str(r.get("question", "")).lower()
            or keyword_lower in str(r.get("answer", "")).lower()
        ):
            results.append(r)
        if len(results) >= 5:
            break
    return results


# ──────────────────────────────────────────────────
# 内部ヘルパー
# ──────────────────────────────────────────────────

def _append_point_log(
    discord_id: str,
    username: str,
    action: str,
    delta: int,
    total_after: int,
    thread_id: Optional[str],
    note: str,
) -> None:
    ws = _sheet("point_log")
    ws.append_row(
        [_now(), discord_id, username, action, delta, total_after, thread_id or "", note],
        value_input_option="USER_ENTERED",
    )


def _now() -> str:
    import pytz
    tz = pytz.timezone(config.TIMEZONE)
    return datetime.datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S")
