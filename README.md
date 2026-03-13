# Teach CLI

综合教学辅助工具平台。

## 可用工具

### 🔖 memory - 记忆管理
基于艾宾浩斯遗忘曲线的知识点记忆管理工具。

**功能特点：**
- 📚 知识点管理：添加、删除、查看知识点
- 🧠 艾宾浩斯遗忘曲线：智能计算复习时间
- 📊 学习阶段追踪：从未学习到已牢记共 9 个阶段
- ⚙️ 可配置：自定义最大复习展示数量

### 🚧 更多工具开发中...
- quiz - 测验工具（计划中）
- schedule - 学习计划（计划中）
- progress - 学习进度追踪（计划中）

## 安装

```bash
cd /root/.openclaw/workspace/dev/teach-cli
pip install -e .
```

安装后会在 `~/.teach/` 目录下创建：
- `memory.db` - SQLite 数据库（memory 工具使用）
- `memory.json` - 配置文件（memory 工具使用）

## 命令结构

```
teach              # 主命令
└── memory         # 记忆管理子命令
    ├── add        # 添加知识点
    ├── list       # 列出知识点
    ├── status     # 查看需要复习的
    ├── remove     # 删除知识点
    ├── study      # 学习/复习
    ├── set        # 设置参数
    └── next       # 下一个待学习
```

## 使用方法

### 添加知识点

```bash
teach memory add "你的知识点内容"
```

### 查看知识点列表

```bash
# 默认显示 20 条
teach memory list

# 显示指定数量
teach memory list -n 50
```

### 查看需要复习的内容

```bash
teach memory status
```

根据艾宾浩斯遗忘曲线，自动计算需要复习的知识点。

### 学习/复习知识点

```bash
teach memory study <知识点 ID>
```

学习后会更新学习时间和阶段。

### 查看下一个待学习知识点

```bash
teach memory next
```

显示第一个未学习的知识点。

### 删除知识点

```bash
teach memory remove <知识点 ID>
```

### 设置参数

```bash
# 查看当前配置
teach memory set

# 设置最大复习展示数量
teach memory set --max 30
```

## 学习阶段

| 阶段 | 说明 | 复习间隔 |
|------|------|----------|
| 未学习 | 新添加的知识点 | - |
| 已学习 | 首次学习完成 | 30 分钟 |
| 第 1 次 | 第 1 次复习后 | 1 小时 |
| 第 2 次 | 第 2 次复习后 | 9 小时 |
| 第 3 次 | 第 3 次复习后 | 1 天 |
| 第 4 次 | 第 4 次复习后 | 2 天 |
| 第 5 次 | 第 5 次复习后 | 6 天 |
| 第 6 次 | 第 6 次复习后 | 30 天 |
| 已牢记 | 已完全掌握 | - |

## 项目结构

```
teach-cli/
├── pyproject.toml      # 项目配置
├── README.md           # 使用说明
└── src/
    └── teach/
        ├── __init__.py # 包初始化
        ├── cli.py      # 主命令行接口
        ├── memory/     # memory 子命令模块
        │   ├── __init__.py
        │   ├── cli.py      # memory 命令实现
        │   ├── database.py # 数据库操作
        │   └── config.py   # 配置管理
        └── [future]/   # 未来其他工具...
```

## 许可证

MIT License
