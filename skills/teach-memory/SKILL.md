# teach-memory 技能

基于艾宾浩斯遗忘曲线的知识点记忆管理工具使用指南。

## 工具概述

`teach memory` 是 Teach CLI 平台的第一个子工具，帮助用户按照艾宾浩斯遗忘曲线科学地管理和复习知识点。

## 安装

```bash
cd /root/.openclaw/workspace/dev/teach-cli
pip install -e .
```

安装后会在 `~/.teach/` 目录创建：
- `memory.db` - SQLite 数据库（存储知识点）
- `memory.json` - 配置文件（管理参数）

## 命令速查

| 命令 | 功能 | 示例 |
|------|------|------|
| `add` | 添加新知识点 | `teach memory add "知识点内容"` |
| `list` | 列举知识点 | `teach memory list -n 20` |
| `status` | 查看需要复习的 | `teach memory status` |
| `remove` | 删除知识点 | `teach memory remove <id>` |
| `study` | 学习/复习知识点 | `teach memory study <id>` |
| `set` | 设置参数 | `teach memory set --max 30` |
| `next` | 下一个待学习 | `teach memory next` |

## 使用流程

### 1. 添加知识点

```bash
teach memory add "Python 列表推导式语法"
teach memory add "Git rebase 和 merge 的区别"
```

输出：
```
✅ 已添加知识点:
   ID: d72ff2ac7872
   内容：Python 列表推导式语法
   状态：未学习
```

### 2. 查看下一个待学习

```bash
teach memory next
```

输出：
```
📖 下一个需要学习的知识点:
   ID: d72ff2ac7872
   内容：Python 列表推导式语法
   创建时间：2026-03-13 15:11
   状态：未学习

💡 使用 'teach memory study d72ff2ac7872' 开始学习
```

### 3. 学习知识点

```bash
teach memory study d72ff2ac7872
```

输出：
```
✅ 已学习知识点:
   ID: d72ff2ac7872
   内容：Python 列表推导式语法
   新阶段：已学习
   学习时间：2026-03-13 15:11
```

### 4. 查看需要复习的

```bash
teach memory status
```

输出：
```
📖 需要复习的知识点 (最多显示 20 条):

  [d72ff2ac7872] Python 列表推导式语法
      当前阶段：已学习 | 上次学习：2026-03-13 14:54
```

### 5. 列出所有知识点

```bash
# 默认显示 20 条
teach memory list

# 显示指定数量
teach memory list -n 50
```

### 6. 删除知识点

```bash
teach memory remove d72ff2ac7872 --yes
```

### 7. 设置参数

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

## 艾宾浩斯遗忘曲线逻辑

1. **添加知识点** → 状态为"未学习"
2. **首次学习** (`study`) → 状态变为"已学习"，30 分钟后需要复习
3. **每次复习** (`study`) → 阶段推进，复习间隔延长
4. **第 6 次复习后** → 状态变为"已牢记"，无需再复习

### 复习计算规则

- `status` 命令根据当前时间和上次学习时间计算是否需要复习
- 超过当前阶段对应的时间间隔 → 需要复习
- 默认最多显示 20 条，可通过 `set --max` 修改
- 超出数量限制时，优先显示 stage 较低的（更需要复习的）

## 最佳实践

### 每日学习流程

```bash
# 1. 早上查看需要复习的
teach memory status

# 2. 逐个复习
teach memory study <id>

# 3. 添加新知识点
teach memory add "今天学的新知识"

# 4. 学习新知识点
teach memory next
teach memory study <id>
```

### 批量添加知识点

```bash
# 可以一次性添加多个
teach memory add "知识点 1"
teach memory add "知识点 2"
teach memory add "知识点 3"

# 然后按顺序学习
teach memory next  # 找到第一个未学习的
teach memory study <id>
```

### 定期清理

```bash
# 查看长期未学习的
teach memory list -n 100

# 删除不再需要记忆的
teach memory remove <id> --yes
```

## 配置说明

配置文件位置：`~/.teach/memory.json`

```json
{
  "max_review": 20
}
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `max_review` | `status` 命令最大展示数量 | 20 |

## 数据存储

- **数据库**: `~/.teach/memory.db` (SQLite)
- **表结构**:
  - `id` - 知识点 ID (12 位 hash)
  - `knowledge` - 知识点内容
  - `created_at` - 创建时间戳
  - `learned_at` - 上次学习时间戳
  - `stage` - 学习阶段 (0-8)

## 常见问题

### Q: 如何备份记忆数据？

```bash
# 备份
cp -r ~/.teach ~/backup/teach-backup-$(date +%Y%m%d)

# 恢复
cp -r ~/backup/teach-backup-* ~/.teach
```

### Q: 如何查看所有数据？

```bash
# 使用 sqlite3 查看
sqlite3 ~/.teach/memory.db "SELECT * FROM memories;"
```

### Q: 误删了怎么办？

如果有备份，从备份恢复。建议定期备份 `~/.teach/` 目录。

### Q: 可以修改已添加的知识点内容吗？

当前版本不支持直接修改。可以：
1. 删除原知识点
2. 重新添加新的

## 版本信息

- **当前版本**: v0.0.1
- **GitHub**: https://github.com/DPamK/teach-cli
- **作者**: 飞少
