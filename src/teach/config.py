"""Configuration management for Teach CLI."""

import json
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    "max_review": 20,  # 最大复习展示数量
}


def get_config_path() -> Path:
    """获取配置文件路径。"""
    home = Path.home()
    teach_dir = home / ".teach"
    teach_dir.mkdir(exist_ok=True)
    return teach_dir / "memory.json"


def load_config() -> Dict[str, Any]:
    """加载配置文件。"""
    config_path = get_config_path()
    
    if not config_path.exists():
        # 创建默认配置
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        # 合并默认配置
        return {**DEFAULT_CONFIG, **config}
    except (json.JSONDecodeError, IOError):
        # 配置文件损坏，使用默认配置
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """保存配置文件。"""
    config_path = get_config_path()
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_max_review() -> int:
    """获取最大复习数量设置。"""
    config = load_config()
    return config.get("max_review", DEFAULT_CONFIG["max_review"])


def set_max_review(value: int) -> None:
    """设置最大复习数量。"""
    config = load_config()
    config["max_review"] = value
    save_config(config)
