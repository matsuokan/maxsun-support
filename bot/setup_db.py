import sys
import logging

# utils/sheets.pyからアクセスするため、configを読み込み可能にしておく
import config
from utils import sheets

logging.basicConfig(level=logging.INFO, format="%(message)s")

def main():
    logging.info("Google Sheets に接続しています...")
    try:
        sh = sheets._get_spreadsheet()
    except Exception as e:
        logging.error(f"接続失敗: {e}")
        sys.exit(1)
        
    logging.info(f"スプレッドシート '{sh.title}' に正常にアクセスしました。")

    sheets_info = {
        "members": ["discord_id", "username", "total_points", "weekly_points", "rank", "solved_count", "reaction_count", "joined_at", "updated_at"],
        "point_log": ["timestamp", "discord_id", "username", "action", "points_delta", "total_after", "thread_id", "note"],
        "rewards_log": ["applied_at", "discord_id", "username", "rank", "reward_type", "reward_detail", "shipping_name", "shipping_address", "email", "status", "shipped_at", "operator", "note"],
        "faq": ["faq_id", "category", "keywords", "question", "answer", "related_thread_id", "created_at", "updated_at", "is_active"],
        "config": ["key", "value", "description"]
    }

    worksheets = {ws.title: ws for ws in sh.worksheets()}
    
    for title, headers in sheets_info.items():
        if title in worksheets:
            logging.info(f"シート '{title}' は既に存在するため、ヘッダーを更新します。")
            ws = worksheets[title]
        else:
            logging.info(f"シート '{title}' を新規作成しています...")
            ws = sh.add_worksheet(title=title, rows=1000, cols=max(20, len(headers)))
        
        # ヘッダー書き込み (gspread 6.1.2 の update は rangeとvaluesをサポート)
        range_str = f"A1:{chr(64 + len(headers))}1"
        ws.update(range_name=range_str, values=[headers])
        ws.format(range_str, {
            "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.2},
            "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
        })
        
    # configのデフォルト値投入
    config_ws = sh.worksheet("config")
    existing_config = config_ws.get_all_values()
    if len(existing_config) <= 1:
        logging.info("config シートに初期設定値を入力しています...")
        defaults = [
            ["points_solved", 20, "/solved 実行時の加算ポイント"],
            ["points_reaction", 1, "👍 リアクション1件あたりの加算ポイント"],
            ["rank_supporter_threshold", 200, "サポーターランクのポイント閾値"],
            ["rank_expert_threshold", 1000, "エキスパートランクのポイント閾値"],
            ["rank_ambassador_threshold", 5000, "アンバサダーランクのポイント閾値"],
            ["weekly_reset_day", "Monday", "週次ポイントリセット曜日"],
            ["ranking_post_day", "Sunday", "ランキング投稿曜日"],
            ["ranking_post_time", "00:00", "ランキング投稿時刻（JST）"]
        ]
        config_ws.update(range_name="A2:C9", values=defaults)

    # デフォルトの不要シート削除
    if "シート1" in worksheets:
        sh.del_worksheet(worksheets["シート1"])
        logging.info("'シート1' を削除しました。")
    if "Sheet1" in worksheets:
        sh.del_worksheet(worksheets["Sheet1"])
        logging.info("'Sheet1' を削除しました。")

    logging.info("スプレッドシートの全自動セットアップが完了しました！！ 🎉")

if __name__ == "__main__":
    main()
