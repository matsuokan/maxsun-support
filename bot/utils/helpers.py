"""
utils/helpers.py - 共通ユーティリティ
"""
from __future__ import annotations

import config


def get_rank_from_points(points: int) -> str:
    """ポイント数からランク文字列を返す。"""
    if points >= config.RANK_THRESHOLDS["ambassador"]:
        return "ambassador"
    elif points >= config.RANK_THRESHOLDS["expert"]:
        return "expert"
    elif points >= config.RANK_THRESHOLDS["supporter"]:
        return "supporter"
    return "helper"


def format_rank_bar(points: int) -> str:
    """次のランクまでの進捗を文字列で返す。"""
    thresholds = [
        ("supporter", config.RANK_THRESHOLDS["supporter"]),
        ("expert", config.RANK_THRESHOLDS["expert"]),
        ("ambassador", config.RANK_THRESHOLDS["ambassador"]),
    ]
    for rank_name, threshold in thresholds:
        if points < threshold:
            remaining = threshold - points
            display = config.RANK_DISPLAY[rank_name]
            return f"{display} まであと **{remaining} pt**（現在: {points} pt）"
    return f"💎 アンバサダー（最高ランク達成！ {points} pt）"


def rank_emoji(rank: str) -> str:
    return config.RANK_DISPLAY.get(rank, rank)
