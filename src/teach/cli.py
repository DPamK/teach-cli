"""Command Line Interface for Teach CLI."""

import click
from datetime import datetime
from typing import Optional

from .database import (
    init_db,
    add_memory,
    list_memories,
    get_memory,
    remove_memory,
    study_memory,
    get_status,
    get_next_unlearned,
    get_all_memories_count,
    STAGES,
)
from .config import load_config, set_max_review, get_max_review


@click.group()
@click.version_option(version="0.0.1", prog_name="teach")
def main():
    """Teach CLI - 综合教学辅助工具平台。
    
    提供多种学习辅助功能，当前可用：
    - memory: 基于艾宾浩斯遗忘曲线的知识点记忆管理
    """
    pass


@main.group()
def memory():
    """记忆管理 - 基于艾宾浩斯遗忘曲线的知识点记忆工具。"""
    pass


@memory.command("add")
@click.argument("knowledge")
def memory_add(knowledge: str):
    """添加新的知识点。
    
    KNOWLEDGE: 要记忆的知识点内容
    """
    conn = init_db()
    try:
        memory_id = add_memory(conn, knowledge)
        click.echo(f"✅ 已添加知识点:")
        click.echo(f"   ID: {memory_id}")
        click.echo(f"   内容：{knowledge}")
        click.echo(f"   状态：未学习")
    finally:
        conn.close()


@memory.command("list")
@click.option("-n", "--limit", default=20, help="显示数量限制（默认 20）")
def memory_list(limit: int):
    """列出已记录的知识点。
    
    -n, --limit: 显示数量限制（默认 20）
    """
    conn = init_db()
    try:
        memories = list_memories(conn, limit)
        total = get_all_memories_count(conn)
        
        if not memories:
            click.echo("📭 暂无知识点记录")
            return
        
        click.echo(f"📚 知识点列表 (共 {total} 条，显示 {len(memories)} 条):\n")
        
        for m in memories:
            stage_name = STAGES[m["stage"]] if m["stage"] < len(STAGES) else f"阶段{m['stage']}"
            created = datetime.fromtimestamp(m["created_at"]).strftime("%Y-%m-%d %H:%M")
            
            click.echo(f"  [{m['id']}] {m['knowledge']}")
            click.echo(f"      状态：{stage_name} | 创建：{created}")
            click.echo()
    finally:
        conn.close()


@memory.command("status")
def memory_status():
    """显示需要复习的知识点。
    
    根据艾宾浩斯遗忘曲线计算需要复习的内容，
    展示数量受配置文件中 max_review 限制。
    """
    conn = init_db()
    try:
        max_review = get_max_review()
        needs_review = get_status(conn, max_review)
        
        if not needs_review:
            click.echo("✅ 暂无需要复习的知识点！")
            return
        
        click.echo(f"📖 需要复习的知识点 (最多显示 {max_review} 条):\n")
        
        for m in needs_review:
            stage_name = STAGES[m["stage"]] if m["stage"] < len(STAGES) else f"阶段{m['stage']}"
            learned = datetime.fromtimestamp(m["learned_at"]).strftime("%Y-%m-%d %H:%M") if m["learned_at"] else "未学习"
            
            click.echo(f"  [{m['id']}] {m['knowledge']}")
            click.echo(f"      当前阶段：{stage_name} | 上次学习：{learned}")
            click.echo()
    finally:
        conn.close()


@memory.command("remove")
@click.argument("memory_id")
@click.confirmation_option(prompt="确定要删除这个知识点吗？")
def memory_remove(memory_id: str):
    """删除指定的知识点。
    
    MEMORY_ID: 要删除的知识点 ID
    """
    conn = init_db()
    try:
        memory = get_memory(conn, memory_id)
        
        if not memory:
            click.echo(f"❌ 未找到 ID 为 {memory_id} 的知识点")
            return
        
        if remove_memory(conn, memory_id):
            click.echo(f"✅ 已删除知识点:")
            click.echo(f"   ID: {memory_id}")
            click.echo(f"   内容：{memory['knowledge']}")
        else:
            click.echo(f"❌ 删除失败")
    finally:
        conn.close()


@memory.command("study")
@click.argument("memory_id")
def memory_study(memory_id: str):
    """学习/复习指定的知识点。
    
    学习后会记录学习时间，并将阶段推进到下一阶段。
    
    MEMORY_ID: 要学习的知识点 ID
    """
    conn = init_db()
    try:
        result = study_memory(conn, memory_id)
        
        if not result:
            click.echo(f"❌ 未找到 ID 为 {memory_id} 的知识点")
            return
        
        stage_name = STAGES[result["stage"]] if result["stage"] < len(STAGES) else f"阶段{result['stage']}"
        learned = datetime.fromtimestamp(result["learned_at"]).strftime("%Y-%m-%d %H:%M")
        
        click.echo(f"✅ 已学习知识点:")
        click.echo(f"   ID: {memory_id}")
        click.echo(f"   内容：{result['knowledge']}")
        click.echo(f"   新阶段：{stage_name}")
        click.echo(f"   学习时间：{learned}")
        
        if result["stage"] >= len(STAGES) - 1:
            click.echo(f"   🎉 恭喜！这个知识点已经牢记！")
    finally:
        conn.close()


@memory.command("set")
@click.option("--max", "max_review", type=int, help="设置最大复习展示数量")
def memory_set(max_review: Optional[int]):
    """设置记忆管理参数。
    
    --max: 设置 status 命令最大展示的复习数量
    """
    if max_review is None:
        # 显示当前配置
        config = load_config()
        click.echo("📋 当前配置:")
        for key, value in config.items():
            click.echo(f"   {key}: {value}")
        return
    
    if max_review < 1:
        click.echo("❌ max_review 必须大于 0")
        return
    
    set_max_review(max_review)
    click.echo(f"✅ 已设置最大复习数量：{max_review}")


@memory.command("next")
def memory_next():
    """显示下一个需要学习的知识点。
    
    按照记录顺序，找到未学习的第一个知识点。
    """
    conn = init_db()
    try:
        next_item = get_next_unlearned(conn)
        
        if not next_item:
            click.echo("✅ 所有知识点都已学习！")
            click.echo("   使用 'teach memory status' 查看需要复习的内容")
            return
        
        created = datetime.fromtimestamp(next_item["created_at"]).strftime("%Y-%m-%d %H:%M")
        
        click.echo(f"📖 下一个需要学习的知识点:")
        click.echo(f"   ID: {next_item['id']}")
        click.echo(f"   内容：{next_item['knowledge']}")
        click.echo(f"   创建时间：{created}")
        click.echo(f"   状态：未学习")
        click.echo()
        click.echo(f"💡 使用 'teach memory study {next_item['id']}' 开始学习")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
