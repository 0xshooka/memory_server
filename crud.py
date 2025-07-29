#!/usr/bin/env python3
"""
Memo CRUD Operations
メモのCRUD操作とJSONファイル管理
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# メモデータファイルのパス
MEMOS_FILE = os.path.join(os.path.dirname(__file__), "memos.json")

def _ensure_memos_file() -> None:
    """
    memos.jsonファイルが存在しなければ空の配列で初期化する
    """
    if not os.path.exists(MEMOS_FILE):
        with open(MEMOS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def _load_memos() -> List[Dict[str, Any]]:
    """
    JSONファイルからメモデータを読み込む
    
    Returns:
        メモのリスト
    """
    _ensure_memos_file()
    try:
        with open(MEMOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # ファイルが破損している場合は空のリストを返す
        return []

def _save_memos(memos: List[Dict[str, Any]]) -> None:
    """
    メモデータをJSONファイルに保存する
    
    Args:
        memos: 保存するメモのリスト
    """
    with open(MEMOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(memos, f, ensure_ascii=False, indent=2)

def _generate_id() -> str:
    """
    ユニークなIDを生成する
    
    Returns:
        UUID4文字列
    """
    return str(uuid.uuid4())

def _get_current_timestamp() -> str:
    """
    現在のタイムスタンプをISO形式で取得する
    
    Returns:
        ISO形式のタイムスタンプ文字列
    """
    return datetime.now(timezone.utc).isoformat()

def _validate_memo_data(content: str, importance: int) -> None:
    """
    メモデータの基本的な検証を行う
    
    Args:
        content: メモの内容
        importance: 重要度
    
    Raises:
        ValueError: 無効なデータの場合
    """
    if not content or not content.strip():
        raise ValueError("メモの内容は必須です")
    
    if not isinstance(importance, int) or importance < 1 or importance > 5:
        raise ValueError("重要度は1から5の整数である必要があります")

def create_memo(
    content: str,
    tags: Optional[List[str]] = None,
    importance: int = 1,
    emotion: Optional[str] = None,
    context: Optional[str] = None,
    related_to: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    新しいメモを作成する
    
    Args:
        content: メモの内容
        tags: タグのリスト
        importance: 重要度（1-5）
        emotion: 感情
        context: 文脈
        related_to: 関連するメモのIDリスト
    
    Returns:
        作成されたメモ
    
    Raises:
        ValueError: 無効なデータの場合
    """
    _validate_memo_data(content, importance)
    
    memo = {
        "id": _generate_id(),
        "content": content.strip(),
        "tags": tags or [],
        "created_at": _get_current_timestamp(),
        "updated_at": _get_current_timestamp(),
        "importance": importance,
        "emotion": emotion,
        "related_to": related_to or [],
        "context": context
    }
    
    memos = _load_memos()
    memos.append(memo)
    _save_memos(memos)
    
    return memo

def get_all_memos() -> List[Dict[str, Any]]:
    """
    すべてのメモを取得する
    
    Returns:
        メモのリスト
    """
    return _load_memos()

def get_memo_by_id(memo_id: str) -> Optional[Dict[str, Any]]:
    """
    指定されたIDのメモを取得する
    
    Args:
        memo_id: メモのID
    
    Returns:
        メモ（見つからない場合はNone）
    """
    memos = _load_memos()
    for memo in memos:
        if memo["id"] == memo_id:
            return memo
    return None

def update_memo(
    memo_id: str,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None,
    importance: Optional[int] = None,
    emotion: Optional[str] = None,
    context: Optional[str] = None,
    related_to: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]:
    """
    既存のメモを更新する
    
    Args:
        memo_id: 更新するメモのID
        content: 新しいメモの内容
        tags: 新しいタグのリスト
        importance: 新しい重要度
        emotion: 新しい感情
        context: 新しい文脈
        related_to: 関連するメモのIDリスト
    
    Returns:
        更新されたメモ（見つからない場合はNone）
    
    Raises:
        ValueError: 無効なデータの場合
    """
    memos = _load_memos()
    
    for i, memo in enumerate(memos):
        if memo["id"] == memo_id:
            # 更新前の検証
            new_content = content if content is not None else memo["content"]
            new_importance = importance if importance is not None else memo["importance"]
            _validate_memo_data(new_content, new_importance)
            
            # フィールドの更新
            if content is not None:
                memo["content"] = content.strip()
            if tags is not None:
                memo["tags"] = tags
            if importance is not None:
                memo["importance"] = importance
            if emotion is not None:
                memo["emotion"] = emotion
            if context is not None:
                memo["context"] = context
            if related_to is not None:
                memo["related_to"] = related_to
            
            # 更新日時を設定
            memo["updated_at"] = _get_current_timestamp()
            
            memos[i] = memo
            _save_memos(memos)
            return memo
    
    return None

def delete_memo(memo_id: str) -> bool:
    """
    指定されたIDのメモを削除する
    
    Args:
        memo_id: 削除するメモのID
    
    Returns:
        削除に成功した場合True、メモが見つからない場合False
    """
    memos = _load_memos()
    
    for i, memo in enumerate(memos):
        if memo["id"] == memo_id:
            # 関連メモから削除対象のIDを除去
            _remove_related_references(memos, memo_id)
            
            # メモを削除
            del memos[i]
            _save_memos(memos)
            return True
    
    return False

def _remove_related_references(memos: List[Dict[str, Any]], deleted_id: str) -> None:
    """
    削除されるメモへの参照を他のメモから除去する
    
    Args:
        memos: メモのリスト
        deleted_id: 削除されるメモのID
    """
    for memo in memos:
        if "related_to" in memo and deleted_id in memo["related_to"]:
            memo["related_to"].remove(deleted_id)
            memo["updated_at"] = _get_current_timestamp()

def search_memos(query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    メモの内容、タグ、文脈から検索する
    
    Args:
        query: 検索クエリ
        limit: 取得件数の上限
    
    Returns:
        検索にマッチしたメモのリスト（重要度順）
    """
    if not query or not query.strip():
        return []
    
    query_lower = query.strip().lower()
    memos = _load_memos()
    matching_memos = []
    
    for memo in memos:
        # 内容での検索
        if query_lower in memo.get("content", "").lower():
            matching_memos.append(memo)
            continue
        
        # タグでの検索
        if any(query_lower in tag.lower() for tag in memo.get("tags", [])):
            matching_memos.append(memo)
            continue
        
        # 文脈での検索
        if memo.get("context") and query_lower in memo["context"].lower():
            matching_memos.append(memo)
            continue
        
        # 感情での検索
        if memo.get("emotion") and query_lower in memo["emotion"].lower():
            matching_memos.append(memo)
            continue
    
    # 重要度順にソート（高い順）
    matching_memos.sort(key=lambda x: x.get("importance", 1), reverse=True)
    
    # 件数制限
    if limit:
        matching_memos = matching_memos[:limit]
    
    return matching_memos

def get_memos_by_tags(tags: List[str]) -> List[Dict[str, Any]]:
    """
    指定されたタグを持つメモを取得する
    
    Args:
        tags: 検索対象のタグリスト
    
    Returns:
        マッチしたメモのリスト
    """
    if not tags:
        return []
    
    memos = _load_memos()
    matching_memos = []
    
    for memo in memos:
        memo_tags = memo.get("tags", [])
        if any(tag in memo_tags for tag in tags):
            matching_memos.append(memo)
    
    # 重要度順にソート
    matching_memos.sort(key=lambda x: x.get("importance", 1), reverse=True)
    return matching_memos

def get_memo_stats() -> Dict[str, Any]:
    """
    メモの統計情報を取得する
    
    Returns:
        統計情報の辞書
    """
    memos = _load_memos()
    
    if not memos:
        return {
            "total_count": 0,
            "tags_count": 0,
            "contexts": [],
            "emotions": [],
            "importance_distribution": {}
        }
    
    # タグの集計
    all_tags = set()
    contexts = set()
    emotions = set()
    importance_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    for memo in memos:
        all_tags.update(memo.get("tags", []))
        if memo.get("context"):
            contexts.add(memo["context"])
        if memo.get("emotion"):
            emotions.add(memo["emotion"])
        importance_dist[memo.get("importance", 1)] += 1
    
    return {
        "total_count": len(memos),
        "tags_count": len(all_tags),
        "unique_tags": sorted(list(all_tags)),
        "contexts": sorted(list(contexts)),
        "emotions": sorted(list(emotions)),
        "importance_distribution": importance_dist
    }
    