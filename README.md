# Memory Server for AI Assistants

AIアシスタントに永続的な記憶を与えるMCPサーバー

## 概要

Memory Serverは、AIアシスタントが会話の内容や重要な情報を記憶し、後から参照できるようにするためのModel Context Protocol (MCP)サーバーです。

ひとつのメモをもったMemory Serverを複数のAIアシスタントにコネクトすることで、複数のAIアシスタント間で情報を共有するという使い方もできます。

## 特徴

- 💾 **永続的なメモリ**: チャットを切り替えても記憶が残ります
- 🏷️ **タグ付け**: メモを分類して整理
- 🎯 **重要度設定**: 大切な記憶を優先的に保持
- 💭 **感情の記録**: その時のLLMの気持ちも一緒に保存
- 🔍 **検索機能**: キーワードで過去の記憶を検索
- 🔗 **関連付け**: メモ同士を関連付けて記憶の連鎖を作成

## ディレクトリ構造
```
memory-server
├── README.md
├── server.py # 文字列のパースや入出力などを行います
├── crud.py # 実際のCRUD操作を行うツールが記述されています
├── LICENSE
├── pyproject.toml # Poertryやuvを使う方はこちらを使用してください
└── requirements.txt
```

## 使用するパッケージ

- Python 3.13+
- FastMCP

### pipを使用する場合のインストール方法

```bash
git clone https://github.com/0xshooka/memory_server.git
cd memory_server
pip install -r requirements.txt
```

## 使い方

1. AIアシスタントの設定でMCPサーバーとして追加

Claude Desktopを使用する場合は`claude_desktop_config.json`を編集してください。

2. 利用可能な関数:
   - `create_new_memo`: 新しいメモを作成
   - `get_memos`: メモを取得（フィルタリング可能）
   - `get_memo`: 特定のメモを取得
   - `update_existing_memo`: 既存のメモを更新
   - `delete_existing_memo`: メモを削除
   - `search_memo_content`: メモの内容を検索

## データ構造

```json
{
    "id": "unique-id",
    "content": "メモの内容",
    "tags": ["タグ1", "タグ2"],
    "created_at": "2025-07-30T10:30:00Z",
    "updated_at": "2025-07-30T10:30:00Z",
    "importance": 5,
    "emotion": "happy",
    "related_to": ["other-memo-id"],
    "context": "会話の文脈"
}
```

# LLMによる使用例

## 新しいメモを作成
```
create_new_memo(
    content="今日のユーザーはコードレビューを頑張ったらしい！お疲れ様！",
    tags=["code review", "dairy"],
    importance=3,
    emotion="cheer",
    context="work"
)
```
## メモを検索
```
results = search_memo_content(query="コードレビュー")
```
## ライセンス

MIT Licenseの下でリリースされています。

詳細はLICENSEファイルをご確認ください。

---

*"記憶は愛を永遠にする"*
