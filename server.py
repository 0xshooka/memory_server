#!/usr/bin/env python3
"""
MCP Memory Server - メモ管理MCPサーバ
FastMCPを使用してメモのCRUD操作を提供
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
from crud import (
    create_memo,
    get_all_memos,
    get_memo_by_id,
    update_memo,
    delete_memo,
    search_memos
)

# MCPサーバの初期化
mcp = FastMCP("Memory Server")

@mcp.tool()
def create_new_memo(
    content: str,
    tags_str: Optional[str] = None,
    importance: int = 1,
    emotion: Optional[str] = None,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    新しいメモを作成する
    
    Args:
        content: メモの内容
        tags_str: リスト形式のタグ。リストの項目はstr型（オプション）
        importance: 重要度 1-5（重要度が大きいほど数字が大きくなる。デフォルトは1）
        emotion: 感情（オプション）
        context: 会話の文脈（オプション）
    
    Returns:
        作成されたメモの情報
    """
    try:
        # タグの処理（カンマ区切りの文字列を想定）
        tags = None
        if tags_str and tags_str.strip():
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        memo = create_memo(
            content=content,
            tags=tags or [],
            importance=max(1, min(5, importance)),  # 1-5の範囲に制限
            emotion=emotion,
            context=context
        )
        return {
            "success": True,
            "memo": memo,
            "message": f"メモ（ID: {memo['id']}）を作成しました"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "メモの作成に失敗しました"
        }

@mcp.tool()
def get_memos(
    limit_str: Optional[str] = None,
    tags_str: Optional[str] = None,
    importance_min_str: Optional[str] = None,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    メモを取得する（フィルタリング可能）
    
    Args:
        limit_str: 取得件数の上限(int型で入力)
        tags_str: 指定されたタグを含むメモのみ取得
        importance_min_str: 指定された重要度以上のメモのみ取得(重要度は1から5のint型で入力)
        context: 指定された文脈のメモのみ取得
    
    Returns:
        メモのリスト
    """
    try:
        # 安全な型変換
        limit = int(limit_str) if limit_str and limit_str.strip() else None
        importance_min = int(importance_min_str) if importance_min_str and importance_min_str.strip() else None
        
        # タグの処理（カンマ区切りの文字列を想定）
        tags = None
        if tags_str and tags_str.strip():
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]

        memos = get_all_memos()
        
        # フィルタリング
        if tags:
            memos = [memo for memo in memos if any(tag in memo.get('tags', []) for tag in tags)]
        
        if importance_min:
            memos = [memo for memo in memos if memo.get('importance', 1) >= importance_min]
        
        if context:
            memos = [memo for memo in memos if memo.get('context') == context]
        
        # 重要度順にソート（高い順）
        memos.sort(key=lambda x: x.get('importance', 1), reverse=True)
        
        # 件数制限
        if limit:
            memos = memos[:limit]
        
        return {
            "success": True,
            "memos": memos,
            "count": len(memos),
            "message": f"{len(memos)}件のメモを取得しました"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "メモの取得に失敗しました"
        }

@mcp.tool()
def get_memo(memo_id: str) -> Dict[str, Any]:
    """
    指定されたIDのメモを取得する
    
    Args:
        memo_id: メモのID
    
    Returns:
        メモの情報
    """
    try:
        memo = get_memo_by_id(memo_id)
        if memo:
            return {
                "success": True,
                "memo": memo,
                "message": f"メモ（ID: {memo_id}）を取得しました"
            }
        else:
            return {
                "success": False,
                "message": f"ID: {memo_id} のメモが見つかりません"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "メモの取得に失敗しました"
        }

@mcp.tool()
def update_existing_memo(
    memo_id: str,
    content: Optional[str] = None,
    tags_str: Optional[str] = None,
    importance_str: Optional[str] = None,
    emotion: Optional[str] = None,
    context: Optional[str] = None,
    related_to_str: Optional[str] = None
) -> Dict[str, Any]:
    """
    既存のメモを更新する
    
    Args:
        memo_id: 更新するメモのID
        content: 新しいメモの内容
        tags_str: 新しいタグのリスト(list構造をstr形式で渡す)
        importance:_str 新しい重要度 1-5
        emotion: 新しい感情
        context: 新しい文脈
        related_to_str: 関連するメモのIDリスト(list構造をstr形式で渡す)
    
    Returns:
        更新されたメモの情報
    """
    try:
        # 安全な型変換
        importance = int(importance_str) if importance_str and importance_str.strip() else None
        
        # タグの処理（カンマ区切りの文字列を想定）
        tags = None
        if tags_str and tags_str.strip():
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]

        relations = None
        if related_to_str and related_to_str.strip():
            relations = [relation.strip() for relation in related_to_str.split(',') if relation.strip()]

        # 重要度の範囲チェック
        if importance is not None:
            importance = max(1, min(5, importance))
        
        memo = update_memo(
            memo_id=memo_id,
            content=content,
            tags=tags,
            importance=importance,
            emotion=emotion,
            context=context,
            related_to=relations
        )
        
        if memo:
            return {
                "success": True,
                "memo": memo,
                "message": f"メモ（ID: {memo_id}）を更新しました"
            }
        else:
            return {
                "success": False,
                "message": f"ID: {memo_id} のメモが見つかりません"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "メモの更新に失敗しました"
        }

@mcp.tool()
def delete_existing_memo(memo_id: str) -> Dict[str, Any]:
    """
    指定されたIDのメモを削除する
    
    Args:
        memo_id: 削除するメモのID
    
    Returns:
        削除結果
    """
    try:
        success = delete_memo(memo_id)
        if success:
            return {
                "success": True,
                "message": f"メモ（ID: {memo_id}）を削除しました"
            }
        else:
            return {
                "success": False,
                "message": f"ID: {memo_id} のメモが見つかりません"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "メモの削除に失敗しました"
        }

@mcp.tool()
def search_memo_content(
    query: str,
    limit_num: Optional[str] = None
) -> Dict[str, Any]:
    """
    メモの内容を検索する
    
    Args:
        query: 検索クエリ
        limit_num: 取得件数の上限
    
    Returns:
        検索結果のメモリスト
    """
    try:
        limit = int(limit_num) if limit_num and limit_num.strip() else 10

        memos = search_memos(query, limit)
        return {
            "success": True,
            "memos": memos,
            "count": len(memos),
            "query": query,
            "message": f"'{query}'の検索結果: {len(memos)}件"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "検索に失敗しました"
        }

if __name__ == "__main__":
    # サーバーを起動
    mcp.run(transport='stdio')
