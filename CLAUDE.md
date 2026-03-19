# CLAUDE.md - MAXSUN コミュニティサポートプロジェクト

このファイルは、Claude（AI）がこのリポジトリで作業する際の指針・コンテキストを提供します。

---

## プロジェクト概要

**MAXSUN** ブランドのマザーボード・グラフィックボードユーザー向けの
Discord ベースのコミュニティサポートシステム。

- 既存ユーザーが新規ユーザーをサポートし、貢献度に応じてノベルティ・クーポンで還元
- Discord Bot + Google Sheets でポイント管理
- 初期フェーズは MAXSUN 社員がサポーター兼運営を担当

詳細 → [`docs/project_overview.md`](docs/project_overview.md)

---

## リポジトリ構成

```
maxsun-support/
├── CLAUDE.md                  # このファイル（AI向け指針）
├── README.md                  # プロジェクト概要（人向け）
├── docs/
│   ├── project_overview.md    # 全体設計・決定事項まとめ
│   ├── discord_design.md      # Discordサーバー・チャンネル設計
│   ├── bot_spec.md            # Discord Bot 仕様
│   ├── sheets_spec.md         # Google Sheets 管理シート設計
│   ├── reward_rules.md        # 貢献ポイント・還元ルール
│   └── community_rules.md    # コミュニティ利用規約
├── bot/                       # Discord Bot 実装（Python）
│   ├── main.py
│   ├── cogs/
│   └── requirements.txt
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md
    │   ├── feature_request.md
    │   └── support_question.md
    └── PULL_REQUEST_TEMPLATE.md
```

---

## 決定済み技術スタック

| 要素 | 採用技術 |
|---|---|
| コミュニティ基盤 | Discord |
| Bot 実装言語 | Python（discord.py） |
| データ管理 | Google Sheets + Google Sheets API |
| バージョン管理 | GitHub（このリポジトリ） |
| 将来的な拡張 | FastAPI / PostgreSQL（未決定） |

---

## 作業ガイドライン

### ブランチ戦略

```
main          # 本番・公開用（直接 push 禁止）
develop       # 開発統合ブランチ
feature/*     # 機能追加
docs/*        # ドキュメント更新
fix/*         # バグ修正
```

### コミットメッセージ規約

```
feat: 新機能の追加
fix:  バグ修正
docs: ドキュメントのみの変更
chore: ビルド・設定変更
refactor: リファクタリング
```

例:
```
feat: /solved コマンドのポイント加算ロジックを実装
docs: Discord サーバー設計ドキュメントを追加
```

### Issues / PR の使い方

- **機能提案・設計変更** → `feature_request` テンプレートで Issue を起票
- **バグ報告** → `bug_report` テンプレートで Issue を起票
- **ドキュメント更新** → `docs/*` ブランチから PR を作成
- PR はレビュアー 1 名以上の Approve を必須とする

---

## Claude への作業依頼時の注意

### 優先事項
1. **日本語でのコミュニケーション**を基本とする
2. 設計変更を伴う提案は必ず `docs/` 配下のドキュメントも同時に更新すること
3. Bot コードを修正する際は `bot/` 配下のファイルを編集する
4. Google Sheets の仕様変更は `docs/sheets_spec.md` を更新してから実装すること

### よく使う作業パターン

**新機能を追加したい場合:**
1. `docs/bot_spec.md` に仕様を追記
2. `bot/cogs/` に実装ファイルを作成
3. `bot/main.py` に登録

**ポイントルールを変更したい場合:**
1. `docs/reward_rules.md` を更新
2. Bot の該当処理を修正

**Discordチャンネルを追加したい場合:**
1. `docs/discord_design.md` を更新
2. README 等に反映

---

## 現在のフェーズ

**Phase 0: 準備中**（2026-03-19〜）

- [x] プロジェクト概要・設計の確定
- [ ] Discord サーバー設計ドキュメント作成
- [ ] Discord Bot 仕様書作成
- [ ] Google Sheets テンプレート設計
- [ ] コミュニティ利用規約草案
- [ ] Bot 実装開始

---

## 関連リンク

- GitHub リポジトリ: https://github.com/matsuokan/maxsun-support
- MAXSUN 公式サイト: https://www.maxsun.com/
- 参考プロジェクト（管理スタイル）: https://github.com/team-mirai/policy
