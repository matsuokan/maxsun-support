# knowledge/ — Discord ナレッジ蓄積ディレクトリ

Bot が毎日 03:00 JST に Discord サーバーの全チャンネルからデータを収集し、
構造化 Markdown として蓄積するディレクトリです。

## ディレクトリ構成

```
knowledge/
├── README.md           ← このファイル
└── daily/
    ├── 2026-03-27/
    │   ├── _metadata.json           ← 収集メタデータ
    │   ├── お知らせ.md
    │   ├── マザーボード-サポート.md
    │   ├── 雑談.md
    │   └── ...
    ├── 2026-03-28/
    │   └── ...
    └── ...
```

## Markdown フォーマット

各ファイルは以下の構造で保存されます。

### テキストチャンネル

```markdown
---
channel: "お知らせ"
channel_id: "1485803370449997906"
category: "📢 お知らせ"
type: text
topic: "MAXSUN からの公式アナウンス"
collected_at: "2026-03-27T03:00:00+09:00"
period_start: "2026-03-26T03:00:00+09:00"
period_end: "2026-03-27T03:00:00+09:00"
message_count: 3
---

# #お知らせ

> MAXSUN からの公式アナウンス

## メッセージ

**MaxsunBot** (ID: 1486250447298760734) `[BOT]` — 2026-03-26T10:00:00+09:00

📢 MAXSUN コミュニティサポートへようこそ！

**リアクション:** 👍 ×3 | 🎉 ×2
```

### フォーラムチャンネル

```markdown
---
channel: "マザーボード-サポート"
channel_id: "1485803381317701852"
category: "❓ テクニカルサポート"
type: forum
topic: "マザーボードに関する質問"
collected_at: "2026-03-27T03:00:00+09:00"
period_start: "2026-03-26T03:00:00+09:00"
period_end: "2026-03-27T03:00:00+09:00"
thread_count: 2
total_messages: 8
---

# #マザーボード-サポート

## スレッド: BIOSが起動しない

| 項目 | 値 |
|---|---|
| 作成者 | Taro_PC |
| 作成日時 | 2026-03-26T10:30:00+09:00 |
| メッセージ数 | 5 |
| 状態 | オープン |
| タグ | 未解決 |

### メッセージ

**Taro_PC** (ID: 123456789) — 2026-03-26T10:30:00+09:00

製品名: MS-B760M POWER
OS: Windows 11 23H2
症状: BIOS画面が表示されない

**リアクション:** なし
```

## 設定（環境変数）

| 変数 | デフォルト | 説明 |
|---|---|---|
| `KNOWLEDGE_COLLECT_HOUR` | `3` | 収集時刻（時、JST） |
| `KNOWLEDGE_COLLECT_MINUTE` | `0` | 収集時刻（分） |
| `KNOWLEDGE_DIR` | `../knowledge/` | 保存先ディレクトリ |
| `KNOWLEDGE_GIT_PUSH` | `false` | 自動 git push を有効化 |

## 管理コマンド

- `/collect-knowledge` — ナレッジ収集を手動で即時実行（管理者のみ）
