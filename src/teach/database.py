"""Database operations for Teach CLI."""

import sqlite3
import hashlib
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

# 艾宾浩斯遗忘曲线复习间隔（小时）
EBBINGHAUS_INTERVALS = [
    0,      # 初始学习
    0.5,    # stage1: 30 分钟
    1,      # stage2: 1 小时
    9,      # stage3: 9 小时
    24,     # stage4: 1 天
    48,     # stage5: 2 天
    144,    # stage6: 6 天
    720,    # stage7: 30 天 - 已牢记
]

# 学习阶段定义
STAGES = [
    "未学习",
    "已学习",
    "第 1 次",
    "第 2 次",
    "第 3 次",
    "第 4 次",
    "第 5 次",
    "第 6 次",
    "已牢记",
]


def get_db_path() -> Path:
    """获取数据库文件路径。"""
    home = Path.home()
    teach_dir = home / ".teach"
    teach_dir.mkdir(exist_ok=True)
    return teach_dir / "memory.db"


def init_db() -> sqlite3.Connection:
    """初始化数据库连接并创建表。"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            knowledge TEXT NOT NULL,
            created_at REAL NOT NULL,
            learned_at REAL,
            stage INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_stage ON memories(stage)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_learned_at ON memories(learned_at)
    """)
    
    conn.commit()
    return conn


def generate_id(knowledge: str, timestamp: float) -> str:
    """根据知识点和时间生成 hash ID。"""
    content = f"{knowledge}:{timestamp}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def add_memory(conn: sqlite3.Connection, knowledge: str) -> str:
    """添加新的知识点。"""
    cursor = conn.cursor()
    timestamp = time.time()
    memory_id = generate_id(knowledge, timestamp)
    
    cursor.execute("""
        INSERT INTO memories (id, knowledge, created_at, learned_at, stage)
        VALUES (?, ?, ?, NULL, 0)
    """, (memory_id, knowledge, timestamp))
    
    conn.commit()
    return memory_id


def list_memories(conn: sqlite3.Connection, limit: int = 20) -> List[Dict[str, Any]]:
    """列出所有知识点。"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, knowledge, created_at, learned_at, stage
        FROM memories
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def get_memory(conn: sqlite3.Connection, memory_id: str) -> Optional[Dict[str, Any]]:
    """根据 ID 获取知识点。"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, knowledge, created_at, learned_at, stage
        FROM memories
        WHERE id = ?
    """, (memory_id,))
    
    row = cursor.fetchone()
    return dict(row) if row else None


def remove_memory(conn: sqlite3.Connection, memory_id: str) -> bool:
    """删除知识点。"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    conn.commit()
    return cursor.rowcount > 0


def study_memory(conn: sqlite3.Connection, memory_id: str) -> Optional[Dict[str, Any]]:
    """学习/复习知识点，更新学习时间和阶段。"""
    cursor = conn.cursor()
    
    # 获取当前状态
    cursor.execute("""
        SELECT id, knowledge, created_at, learned_at, stage
        FROM memories
        WHERE id = ?
    """, (memory_id,))
    
    row = cursor.fetchone()
    if not row:
        return None
    
    current_stage = row["stage"]
    # 阶段推进（最大到 8=已牢记）
    new_stage = min(current_stage + 1, 8)
    new_learned_at = time.time()
    
    cursor.execute("""
        UPDATE memories
        SET learned_at = ?, stage = ?
        WHERE id = ?
    """, (new_learned_at, new_stage, memory_id))
    
    conn.commit()
    
    return {
        "id": memory_id,
        "knowledge": row["knowledge"],
        "created_at": row["created_at"],
        "learned_at": new_learned_at,
        "stage": new_stage,
    }


def get_status(conn: sqlite3.Connection, max_review: int = 20) -> List[Dict[str, Any]]:
    """获取需要复习的知识点列表。"""
    cursor = conn.cursor()
    current_time = time.time()
    
    # 查询所有已学习的知识点（stage > 0 且 stage < 8）
    cursor.execute("""
        SELECT id, knowledge, created_at, learned_at, stage
        FROM memories
        WHERE stage > 0 AND stage < 8
        ORDER BY stage ASC, learned_at ASC
    """)
    
    rows = cursor.fetchall()
    needs_review = []
    
    for row in rows:
        stage = row["stage"]
        learned_at = row["learned_at"]
        
        if learned_at is None:
            continue
        
        # 计算距离上次学习的时间（小时）
        hours_since_learned = (current_time - learned_at) / 3600
        
        # 获取当前阶段应该复习的时间间隔
        if stage < len(EBBINGHAUS_INTERVALS):
            interval = EBBINGHAUS_INTERVALS[stage]
            
            # 如果已经超过间隔时间，需要复习
            if hours_since_learned >= interval:
                needs_review.append(dict(row))
    
    # 按 max_review 限制返回数量
    return needs_review[:max_review]


def get_next_unlearned(conn: sqlite3.Connection) -> Optional[Dict[str, Any]]:
    """获取下一个未学习的知识点。"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, knowledge, created_at, learned_at, stage
        FROM memories
        WHERE stage = 0
        ORDER BY created_at ASC
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    return dict(row) if row else None


def get_all_memories_count(conn: sqlite3.Connection) -> int:
    """获取所有知识点数量。"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM memories")
    return cursor.fetchone()[0]
