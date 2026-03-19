# Discord Bot 仕様書

**プロジェクト**: MAXSUN コミュニティサポート  
**Bot 名**: MaxBot（仮称）  
**実装言語**: Python 3.11 / discord.py 2.x  
**データストア**: Google Sheets（Sheets API v4）  
**作成日**: 2026-03-20

---

## 1. Bot の役割概要

| 役割 | 内容 |
|---|---|
| ポイント管理 | 回答・解決済みマーク・リアクションによるポイントの自動加算 |
| ランク管理 | ポイント閾値到達時のロール自動昇格 |
| 報酬申請受付 | ランク到達者のクーポン・ノベルティ申請の受付 |
| 情報提供 | ユーザーへのポイント確認・FAQ案内 |
| 運営支援 | 週次ランキング投稿・モデレーションログ |

---

## 2. スラッシュコマンド一覧

### ユーザー向けコマンド

| コマンド | 引数 | 説明 | 実行可能チャンネル |
|---|---|---|---|
| `/solved` | なし | 自分のスレッドを解決済みにし、最終回答者に +20 pt 加算 | サポートスレッド内のみ |
| `/mypoints` | なし | 自分の累計ポイント・ランク・次のランクまでの差分を表示（本人のみ見えるEphemeral） | 全チャンネル |
| `/leaderboard` | なし | ポイント上位10名を表示（Ephemeral） | 全チャンネル |
| `/reward-apply` | なし | 報酬申請フォームを表示（ランク条件を満たしている場合のみ） | `#受け取り申請` のみ |
| `/faq` | `keyword` | キーワードで FAQ を検索して表示（Ephemeral） | 全チャンネル |

### 運営向けコマンド（`👑 MAXSUN公式` ロールのみ）

| コマンド | 引数 | 説明 |
|---|---|---|
| `/add-points` | `@user` `amount` `reason` | 手動でポイントを加算（ノベルティ贈呈等のボーナス用） |
| `/remove-points` | `@user` `amount` `reason` | ポイントをペナルティで減算（不正対策） |
| `/set-rank` | `@user` `rank` | ランクを手動で設定 |
| `/reward-complete` | `@user` | 報酬発送完了をマーク（Sheets に記録） |
| `/post-ranking` | なし | 週次ランキングを即時投稿 |
| `/userinfo` | `@user` | ユーザーのポイント・ランク・履歴を確認 |

---

## 3. 自動イベント（コマンド以外）

### 3-A. フォーラムスレッド作成時（質問テンプレート自動表示）

**トリガー**: サポートカテゴリのフォーラムチャンネルで新規スレッド作成  
**動作**: Bot がスレッドに以下のメッセージを自動投稿

```
📋 **質問テンプレート**

回答者が理解しやすいよう、以下を埋めてください：

■ 製品名・型番：（例: MS-RX7900XT GAMING X 24G）
■ OS・バージョン：（例: Windows 11 23H2）
■ 症状・問題：
■ 試したこと：
■ エラーメッセージ（あれば）：

解決したら `/solved` コマンドを実行してください ✅
```

### 3-B. /solved 実行時のポイント加算ロジック

```
質問者が /solved を実行
  ├─ スレッドの最後のメッセージ投稿者 = 回答者？
  │    → 回答者に +20 pt 加算
  ├─ 複数の回答者がいる場合
  │    → 直前のメッセージ投稿者に +20 pt（将来的に複数選択も検討）
  ├─ 質問者 = 回答者 の場合（自作自演）
  │    → エラーメッセージを表示（ポイント加算なし）
  └─ スレッドに「解決済み」タグを付与してクローズ
```

### 3-C. 👍 リアクション時

**トリガー**: サポートチャンネル内のメッセージに 👍 リアクション  
**動作**:
- 投稿者に +1 pt 加算（同一メッセージへの同一ユーザーの 👍 は1回のみカウント）
- 自分自身のメッセージへの 👍 はカウントしない

### 3-D. ランク自動昇格

**トリガー**: ポイント加算後にしきい値チェック

| しきい値 | 変化 |
|---|---|
| 200 pt 到達 | 🥉→🥈 サポーターに昇格・通知を `#ポイントランキング` に投稿 |
| 1,000 pt 到達 | 🥈→🥇 エキスパートに昇格・通知を投稿 |
| 5,000 pt 到達 | 🥇→💎 アンバサダーに昇格・通知を投稿 |

昇格通知メッセージ例:
```
🎉 @username さんがランクアップしました！
🥈 サポーター（200 pt 達成）

/reward-apply コマンドでノベルティを申請できます。
```

### 3-E. 週次ランキング自動投稿

**トリガー**: 毎週日曜 0:00 JST  
**投稿先**: `#ポイントランキング`  
**内容**: 週間獲得ポイント上位10名 + 累計上位10名

---

## 4. Google Sheets 連携仕様

### シート構成

#### `members` シート

| 列 | カラム名 | 型 | 説明 |
|---|---|---|---|
| A | discord_id | string | Discord ユーザー ID（一意キー） |
| B | username | string | Discord 表示名 |
| C | total_points | integer | 累計ポイント |
| D | weekly_points | integer | 当週獲得ポイント（毎週リセット） |
| E | rank | string | 現在のランク（helper/supporter/expert/ambassador） |
| F | joined_at | datetime | サーバー参加日時 |
| G | updated_at | datetime | 最終更新日時 |

#### `point_log` シート

| 列 | カラム名 | 型 | 説明 |
|---|---|---|---|
| A | timestamp | datetime | 発生日時 |
| B | discord_id | string | 対象ユーザー ID |
| C | action | string | アクション種別（solved/reaction/bonus/penalty） |
| D | points | integer | 加減算ポイント（マイナスはペナルティ） |
| E | reason | string | 理由・補足（スレッドIDや運営メモ） |

#### `rewards_log` シート

| 列 | カラム名 | 型 | 説明 |
|---|---|---|---|
| A | applied_at | datetime | 申請日時 |
| B | discord_id | string | 申請者 Discord ID |
| C | username | string | 申請者名 |
| D | rank | string | 申請時のランク |
| E | reward_type | string | 報酬種別（coupon / novelty） |
| F | status | string | ステータス（pending / shipped / completed） |
| G | shipped_at | datetime | 発送日時 |
| H | note | string | 運営メモ |

---

## 5. ポイントルール詳細

| アクション | 加算 pt | 条件 |
|---|---|---|
| `/solved` で解決済みマーク | +20 | 質問者が実行、回答者に付与 |
| 回答投稿（解決に至らなかった場合） | +0 | `/solved` 実行時のみポイント発生 |
| 👍 リアクションをもらう | +1 | 同一メッセージ・同一ユーザーから1回まで |
| 運営ボーナス（特別貢献） | 任意 | `/add-points` で運営が手動付与 |
| 誤情報・ルール違反（ペナルティ） | −10 | `/remove-points` で運営が手動減算 |

---

## 6. プロジェクト構成（ファイル）

```
bot/
├── main.py                  # Bot 起動・Cog 登録
├── config.py                # 設定値（チャンネルID・シートID等）
├── requirements.txt         # 依存パッケージ
├── cogs/
│   ├── support.py           # /solved・フォーラム自動テンプレート
│   ├── points.py            # ポイント加算・リアクション検知
│   ├── ranks.py             # ランク昇格ロジック
│   ├── rewards.py           # /reward-apply・報酬申請受付
│   ├── info.py              # /mypoints・/leaderboard・/faq
│   ├── admin.py             # 運営向けコマンド
│   └── scheduler.py         # 週次ランキング投稿・週次ポイントリセット
└── utils/
    ├── sheets.py            # Google Sheets API ラッパー
    └── helpers.py           # 共通ユーティリティ
```

---

## 7. 環境変数・設定

`.env` ファイルで管理（Git 管理外）:

```env
# Discord
DISCORD_TOKEN=xxxxxxxxxxxxxxxxxx

# Google Sheets
GOOGLE_SHEETS_ID=xxxxxxxxxxxxxxxxxx
GOOGLE_SERVICE_ACCOUNT_JSON=./credentials.json

# チャンネル ID
CHANNEL_RANKING=000000000000000000
CHANNEL_REWARD_APPLY=000000000000000000
CHANNEL_MOD_LOG=000000000000000000

# ロール ID
ROLE_HELPER=000000000000000000
ROLE_SUPPORTER=000000000000000000
ROLE_EXPERT=000000000000000000
ROLE_AMBASSADOR=000000000000000000
ROLE_STAFF=000000000000000000
```

---

## 8. Bot 権限設定（Discord Developer Portal）

### OAuth2 スコープ
- `bot`
- `applications.commands`

### Bot 権限
- `Manage Roles`（ランク昇格のロール付与）
- `Send Messages`
- `Send Messages in Threads`
- `Create Public Threads`
- `Manage Messages`（解決済みスレッドのタグ付け）
- `Add Reactions`
- `Read Message History`
- `View Channels`

---

## 9. 開発・運用フロー

### セットアップ手順

```bash
# 1. リポジトリをクローン
git clone https://github.com/matsuokan/maxsun-support.git
cd maxsun-support/bot

# 2. 依存パッケージをインストール
pip install -r requirements.txt

# 3. .env を作成（テンプレートをコピー）
cp .env.example .env
# → .env に各種トークン・ID を記入

# 4. Google サービスアカウントの認証情報を配置
# credentials.json を bot/ ディレクトリに配置

# 5. テスト用サーバーで起動確認
python main.py
```

### デプロイ先（案）

| 環境 | 用途 | 候補 |
|---|---|---|
| 開発 | ローカル or テストサーバー | 開発者のローカルPC |
| 本番 | 常時稼働 | Railway / Render / VPS（さくらクラウド等） |

---

*関連ドキュメント: [プロジェクト概要](project_overview.md) | [Discord設計](discord_design.md) | [Sheets仕様](sheets_spec.md)*
