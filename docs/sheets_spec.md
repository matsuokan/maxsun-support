# Google Sheets 管理シート設計書

**プロジェクト**: MAXSUN コミュニティサポート  
**作成日**: 2026-03-20  
**用途**: Discord Bot によるポイント管理・報酬管理のデータストア

---

## 1. スプレッドシート構成

| シート名 | 用途 | 主な操作者 |
|---|---|---|
| `members` | ユーザー情報・累計ポイント・ランク管理 | Bot（自動） |
| `point_log` | ポイント加算・減算の全履歴 | Bot（自動） |
| `rewards_log` | 報酬申請・発送状況の管理 | Bot（申請）・運営（発送処理） |
| `faq` | FAQ コンテンツ管理（`/faq` コマンド用） | 運営（手動更新） |
| `config` | ポイントルール・閾値等の設定値 | 運営（手動変更） |

---

## 2. `members` シート

> ユーザー1人につき1行。Bot が自動で行を追加・更新する。

### 列定義

| 列 | カラム名 | 型 | 必須 | 説明 |
|---|---|---|---|---|
| A | `discord_id` | string | ✅ | Discord ユーザー ID（不変の一意キー） |
| B | `username` | string | ✅ | Discord 表示名（変更時に自動更新） |
| C | `total_points` | integer | ✅ | 累計ポイント（初期値: 0） |
| D | `weekly_points` | integer | ✅ | 当週獲得ポイント（毎週月曜 0:00 JST に自動リセット） |
| E | `rank` | string | ✅ | 現在のランク（`helper` / `supporter` / `expert` / `ambassador`） |
| F | `solved_count` | integer | ✅ | 解決済みマーク獲得回数（`/solved` で加点された回数） |
| G | `reaction_count` | integer | ✅ | 👍 リアクション獲得回数の累計 |
| H | `joined_at` | datetime | ✅ | Discord サーバー参加日時（ISO 8601） |
| I | `updated_at` | datetime | ✅ | 最終更新日時（ISO 8601） |

### サンプルデータ

| A (discord_id) | B (username) | C (total_points) | D (weekly_points) | E (rank) | F (solved_count) | G (reaction_count) | H (joined_at) | I (updated_at) |
|---|---|---|---|---|---|---|---|---|
| 123456789012345678 | Taro_PC | 1250 | 80 | expert | 55 | 200 | 2026-03-01T10:00:00 | 2026-03-20T00:00:00 |
| 234567890123456789 | Hanako_Build | 320 | 40 | supporter | 14 | 48 | 2026-03-05T14:30:00 | 2026-03-19T22:00:00 |

---

## 3. `point_log` シート

> ポイント変動の全履歴。Bot が自動で行を追記する（削除・編集不可）。

### 列定義

| 列 | カラム名 | 型 | 必須 | 説明 |
|---|---|---|---|---|
| A | `timestamp` | datetime | ✅ | 発生日時（ISO 8601, JST） |
| B | `discord_id` | string | ✅ | 対象ユーザーの Discord ID |
| C | `username` | string | ✅ | 対象ユーザーの表示名（記録時点） |
| D | `action` | string | ✅ | アクション種別（下記参照） |
| E | `points_delta` | integer | ✅ | 加減算ポイント（減算はマイナス） |
| F | `total_after` | integer | ✅ | 加算後の累計ポイント |
| G | `thread_id` | string | | 関連スレッド ID（`/solved` ・リアクション時） |
| H | `note` | string | | 補足メモ（運営手動操作時の理由等） |

### `action` 種別

| 値 | 説明 | 加算 pt |
|---|---|---|
| `solved` | `/solved` で解決済みマーク（他者の質問を解決） | +20 |
| `reaction_received` | 👍 リアクションをもらった | +1 |
| `bonus` | 運営による手動ボーナス付与 | 任意 |
| `penalty` | 運営による手動ペナルティ | 任意（マイナス） |

### サンプルデータ

| A (timestamp) | B (discord_id) | C (username) | D (action) | E (points_delta) | F (total_after) | G (thread_id) | H (note) |
|---|---|---|---|---|---|---|---|
| 2026-03-20T00:05:00 | 123456789012345678 | Taro_PC | solved | +20 | 1250 | 1234567890 | |
| 2026-03-20T00:10:00 | 123456789012345678 | Taro_PC | reaction_received | +1 | 1251 | | |
| 2026-03-19T15:00:00 | 234567890123456789 | Hanako_Build | bonus | +50 | 320 | | FAQ記事投稿ありがとう |

---

## 4. `rewards_log` シート

> 報酬申請の受付・発送状況を管理。Bot が申請行を追記し、運営がステータスを手動更新する。

### 列定義

| 列 | カラム名 | 型 | 必須 | 説明 |
|---|---|---|---|---|
| A | `applied_at` | datetime | ✅ | 申請日時（ISO 8601） |
| B | `discord_id` | string | ✅ | 申請者の Discord ID |
| C | `username` | string | ✅ | 申請者の表示名 |
| D | `rank` | string | ✅ | 申請時のランク |
| E | `reward_type` | string | ✅ | 報酬種別（`coupon` / `novelty`） |
| F | `reward_detail` | string | ✅ | 報酬の具体的な内容（クーポンコード等） |
| G | `shipping_name` | string | ✅ | 送付先氏名（ノベルティの場合） |
| H | `shipping_address` | string | | 送付先住所（ノベルティの場合） |
| I | `email` | string | ✅ | 送付先メールアドレス（クーポンの場合） |
| J | `status` | string | ✅ | ステータス（`pending` / `processing` / `shipped` / `completed` / `cancelled`） |
| K | `shipped_at` | datetime | | 発送・送付日時 |
| L | `operator` | string | | 処理担当者名（運営が記入） |
| M | `note` | string | | 運営メモ |

### ステータス遷移

```
pending（申請受付）
  → processing（運営が処理開始）
    → shipped（発送済み・メール送信済み）
      → completed（受取確認）
  or → cancelled（キャンセル・不正等）
```

---

## 5. `faq` シート

> `/faq <keyword>` コマンドの検索ソース。運営が手動でメンテナンスする。

### 列定義

| 列 | カラム名 | 型 | 必須 | 説明 |
|---|---|---|---|---|
| A | `faq_id` | string | ✅ | 一意の FAQ ID（例: `mb-001`） |
| B | `category` | string | ✅ | カテゴリ（`motherboard` / `gpu` / `bios` / `compatibility`） |
| C | `keywords` | string | ✅ | 検索キーワード（カンマ区切り） |
| D | `question` | string | ✅ | 質問文 |
| E | `answer` | string | ✅ | 回答文（Markdown 記法可） |
| F | `related_thread_id` | string | | 元となった解決済みスレッド ID |
| G | `created_at` | datetime | ✅ | 作成日時 |
| H | `updated_at` | datetime | ✅ | 最終更新日時 |
| I | `is_active` | boolean | ✅ | 有効フラグ（FALSE で非表示） |

---

## 6. `config` シート

> Bot の動作に関するルール・設定値。ここを変更するだけで Bot の挙動を調整できる。

### 列定義

| 列 | カラム名 | 説明 |
|---|---|---|
| A | `key` | 設定キー名 |
| B | `value` | 設定値 |
| C | `description` | 説明（運営メモ） |

### 初期設定値

| key | value | description |
|---|---|---|
| `points_solved` | 20 | /solved 実行時の加算ポイント |
| `points_reaction` | 1 | 👍 リアクション1件あたりの加算ポイント |
| `rank_supporter_threshold` | 200 | サポーターランクのポイント閾値 |
| `rank_expert_threshold` | 1000 | エキスパートランクのポイント閾値 |
| `rank_ambassador_threshold` | 5000 | アンバサダーランクのポイント閾値 |
| `weekly_reset_day` | Monday | 週次ポイントリセット曜日 |
| `ranking_post_day` | Sunday | ランキング投稿曜日 |
| `ranking_post_time` | 00:00 | ランキング投稿時刻（JST） |

---

## 7. シート操作の権限設定

| 対象 | 権限 |
|---|---|
| Bot サービスアカウント | 全シートの読み取り・書き込み |
| 運営（MAXSUN 社員） | 全シートの読み取り・書き込み |
| `rewards_log` の個人情報列（G〜I） | 閲覧は担当者のみに制限（列を非表示にし、運営のみアクセス） |

> [!IMPORTANT]
> `rewards_log` の住所・メールアドレスは個人情報です。
> Google Sheets の「保護された範囲」機能を使い、担当者以外が閲覧できないよう設定してください。

---

## 8. スプレッドシート作成手順（初期セットアップ）

1. Google Sheets で新規スプレッドシートを作成
2. スプレッドシート名を `MAXSUN-Support-DB` に設定
3. 各シートタブを以下の順で作成：`members` / `point_log` / `rewards_log` / `faq` / `config`
4. 各シートの1行目にヘッダー行を設定（太字・背景色で視認性UP）
5. Google Cloud Console でサービスアカウントを作成し、`credentials.json` を発行
6. スプレッドシートをサービスアカウントのメールアドレスと共有（編集者権限）
7. `config` シートに初期設定値を記入
8. `bot/config.py` の `GOOGLE_SHEETS_ID` にスプレッドシート ID を設定

---

*関連ドキュメント: [プロジェクト概要](project_overview.md) | [Bot仕様](bot_spec.md) | [Discord設計](discord_design.md)*
