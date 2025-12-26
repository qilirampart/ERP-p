# Claude Code 常用命令手册

> 快速参考指南 - 最后更新：2025-12-08

## 📋 目录

- [基础命令](#基础命令)
- [会话管理](#会话管理)
- [模型选择](#模型选择)
- [MCP 服务器](#mcp-服务器)
- [权限配置](#权限配置)
- [斜杠命令](#斜杠命令)
- [钩子配置](#钩子配置)
- [调试和输出](#调试和输出)
- [快捷键](#快捷键)
- [配置文件](#配置文件)

---

## 🚀 基础命令

### 启动会话

```bash
# 基本启动（当前目录）
claude

# 指定项目目录启动
claude /path/to/project

# 使用特定模型启动
claude --model opus

# 非交互模式（管道输出）
claude --print "你的问题"
```

### 常用选项

```bash
-h, --help              # 显示帮助信息
-v, --version          # 显示版本号
-d, --debug            # 启用调试模式
--verbose              # 详细输出
-p, --print            # 打印模式（非交互）
```

---

## 💬 会话管理

### 继续和恢复会话

```bash
# 继续最近的会话（最常用）
claude -c
claude --continue

# 恢复特定会话（交互式选择器）
claude -r
claude --resume

# 恢复特定会话（指定ID）
claude --resume <session-id>

# 恢复时搜索关键词
claude --resume "ERP项目"

# Fork 会话（创建分支）
claude --fork-session --resume <session-id>
```

### 会话操作

```bash
# 使用特定会话ID
claude --session-id <uuid>

# 创建新会话ID而非复用
claude --fork-session --continue
```

**使用场景：**
- `--continue`: 中断后立即继续
- `--resume`: 查看并选择历史会话
- `--fork-session`: 从某个会话点创建新分支

---

## 🤖 模型选择

### 可用模型

```bash
# Sonnet 4.5（默认，平衡速度和能力）
claude --model sonnet

# Opus 4.5（最强能力）
claude --model opus

# Haiku 4.5（最快速）
claude --model haiku

# 完整模型名
claude --model claude-sonnet-4-5-20250929
```

### 模型对比

| 别名 | 完整名称 | 特点 | 推荐用途 |
|------|----------|------|----------|
| `sonnet` | claude-sonnet-4-5-20250929 | 平衡 | 日常开发 |
| `opus` | claude-opus-4-5-20251101 | 最强 | 复杂任务 |
| `haiku` | claude-haiku-4-5-20251001 | 快速 | 简单查询 |

---

## 🔌 MCP 服务器

### 已配置的 MCP 服务器

你当前配置的服务器（在 `%APPDATA%\Claude\mcp-config.json`）：

```json
{
  "servers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-chrome-devtools"]
    }
  }
}
```

### 常用 MCP 服务器

```bash
# Chrome DevTools（已配置）
npx @modelcontextprotocol/server-chrome-devtools

# Git 集成
npx @modelcontextprotocol/server-git

# 文件系统访问
npx @modelcontextprotocol/server-filesystem

# Web 浏览器
npx @modelcontextprotocol/server-web-browser

# SQLite 数据库
npx @modelcontextprotocol/server-sqlite
```

### 配置示例

```json
{
  "servers": {
    "git": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-git"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_PATHS": "C:\\Project,C:\\Documents"
      }
    }
  }
}
```

### MCP 命令选项

```bash
# 指定 MCP 配置文件
claude --mcp-config path/to/config.json

# 仅使用指定的 MCP 配置
claude --strict-mcp-config --mcp-config custom.json

# 启用 MCP 调试
claude --debug
```

---

## 🔐 权限配置

### 你的当前配置

位置：`.claude/settings.local.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(powershell -Command ...)",
      "Bash(tree:*)",
      "Bash(mkdir:*)",
      "Bash(npm:*)",
      "Bash(git:*)",
      "Bash(poetry:*)",
      "Bash(python:*)",
      "Bash(pip:*)",
      "Bash(dir:*)",
      "Bash(curl:*)",
      "Bash(cat:*)"
    ]
  }
}
```

### 权限模式

```bash
# 允许特定工具（无需询问）
"allow": ["Bash(npm install:*)"]

# 禁止特定工具
"deny": ["Bash(rm:*)", "Bash(sudo:*)"]

# 每次询问
"ask": ["Bash(curl:*)", "Bash(wget:*)"]
```

### 通配符使用

```bash
Bash(git:*)              # 允许所有 git 命令
Bash(npm install:*)      # 允许 npm install
Bash(tree:*)             # 允许 tree 命令
```

### 命令行权限选项

```bash
# 允许特定工具
claude --allowed-tools "Bash(git:*) Edit Read"

# 禁止特定工具
claude --disallowed-tools "Bash(rm:*) Write"

# 跳过所有权限检查（危险）
claude --dangerously-skip-permissions

# 设置权限模式
claude --permission-mode acceptEdits
claude --permission-mode dontAsk
```

---

## ⚡ 斜杠命令

### 内置命令

```bash
/help                    # 显示帮助
/clear                   # 清屏
```

### 你的自定义命令

位置：`.claude/commands/`

```bash
/init                    # 初始化 CLAUDE.md 文件
/pr-comments            # 获取 GitHub PR 注释
/statusline             # 设置状态栏配置
/review                 # 代码审查
/security-review        # 安全审查
```

### 创建自定义命令

在 `.claude/commands/` 目录下创建 `.md` 文件：

```bash
# .claude/commands/test.md
运行项目测试套件并报告结果
```

使用：
```bash
/test
```

---

## 🪝 钩子配置

### 什么是钩子？

钩子允许在工具调用前后执行自定义脚本。

### 配置位置

`.claude/settings.local.json` 中添加：

```json
{
  "hooks": {
    "pre-tool-use": {
      "Bash": ["echo '执行命令前...'"]
    },
    "post-tool-use": {
      "Bash": ["echo '命令执行完成'"]
    }
  }
}
```

### 常用钩子示例

```json
{
  "hooks": {
    "pre-tool-use": {
      "Bash(git commit:*)": ["npm run lint"],
      "Write": ["echo '准备写入文件...'"]
    },
    "post-tool-use": {
      "Bash(npm install:*)": ["echo '依赖安装完成'"],
      "Bash(git commit:*)": ["npm test"]
    }
  }
}
```

---

## 🐛 调试和输出

### 调试模式

```bash
# 启用调试日志
claude --debug

# 过滤调试类别
claude --debug "api,hooks"

# 排除特定类别
claude --debug "!statsig,!file"

# 详细模式
claude --verbose
```

### 输出格式

```bash
# 文本输出（默认）
claude --print "问题" --output-format text

# JSON 输出
claude --print "问题" --output-format json

# 流式 JSON
claude --print "问题" --output-format stream-json

# 包含部分消息
claude --print "问题" --output-format stream-json --include-partial-messages
```

### JSON Schema 结构化输出

```bash
claude --print "生成用户数据" --json-schema '{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "age": {"type": "number"}
  },
  "required": ["name", "age"]
}'
```

---

## ⌨️ 快捷键

### 交互式会话中

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+C` | 中断当前操作 |
| `Ctrl+D` | 退出会话 |
| `Ctrl+L` | 清屏 |
| `↑` / `↓` | 浏览命令历史 |
| `Tab` | 自动完成（如果支持） |

### Windows 特定

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+V` | 粘贴 |
| `Ctrl+C` | 复制（未选中文本时中断） |

---

## 📁 配置文件

### 配置文件位置

```
全局配置（用户级）
Windows: %APPDATA%\Claude\
  ├── mcp-config.json          # MCP 服务器配置
  └── settings.json             # 全局设置

项目配置（项目级）
项目根目录/.claude/
  ├── settings.local.json       # 本地设置（已配置）
  ├── commands/                 # 斜杠命令
  │   ├── init.md
  │   ├── pr-comments.md
  │   ├── review.md
  │   └── security-review.md
  └── CLAUDE.md                 # 项目文档
```

### 你的当前配置

#### `.claude/settings.local.json`

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "code-switch",
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:18100"
  },
  "permissions": {
    "allow": [
      "Bash(powershell -Command \"Get-ChildItem -Path 'C:\\Project\\ERP-backend-py' -Force -Recurse | Select-Object FullName | ConvertTo-Csv -NoTypeInformation\")",
      "Bash(tree:*)",
      "Bash(mkdir:*)",
      "Bash(npm create:*)",
      "Bash(npm install:*)",
      "Bash(npx tailwindcss init -p)",
      "Bash(git config:*)",
      "Bash(git init:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git remote add:*)",
      "Bash(git branch:*)",
      "Bash(git push:*)",
      "Bash(sc query:*)",
      "Bash(poetry --version:*)",
      "Bash(pip install:*)",
      "Bash(poetry install:*)",
      "Bash(python3.10:*)",
      "Bash(python3.11:*)",
      "Bash(python3.12:*)",
      "Bash(py:*)",
      "Bash(poetry env use:*)",
      "Bash(dir:*)",
      "Bash(poetry run alembic:*)",
      "Bash(poetry run python:*)",
      "Bash(poetry run uvicorn:*)",
      "Bash(curl:*)",
      "Bash(cat:*)"
    ],
    "deny": [],
    "ask": []
  }
}
```

### 加载配置选项

```bash
# 从文件加载设置
claude --settings path/to/settings.json

# 从 JSON 字符串加载
claude --settings '{"model":"opus"}'

# 指定配置源
claude --setting-sources "user,project,local"
```

---

## 🔧 高级选项

### 工具控制

```bash
# 指定可用工具
claude --print "问题" --tools "Bash,Edit,Read"

# 禁用所有工具
claude --print "问题" --tools ""

# 使用默认工具集
claude --print "问题" --tools "default"
```

### 目录访问

```bash
# 添加额外的访问目录
claude --add-dir C:\Projects --add-dir C:\Documents

# IDE 自动连接
claude --ide
```

### 插件管理

```bash
# 加载插件目录
claude --plugin-dir path/to/plugins

# 查看插件
claude plugin list

# 安装插件
claude plugin install plugin-name
```

---

## 📚 常见使用场景

### 1. 快速继续上次中断的工作

```bash
claude -c
```

### 2. 在项目中开始新会话

```bash
cd C:\Project\ERP-p
claude
```

### 3. 使用强大模型处理复杂问题

```bash
claude --model opus
```

### 4. 非交互模式运行脚本

```bash
claude --print "分析这个文件" < input.txt > output.txt
```

### 5. 调试权限问题

```bash
claude --debug "permissions"
```

### 6. 获取 JSON 格式输出

```bash
claude --print "生成配置" --output-format json
```

---

## 🆘 获取帮助

```bash
# 查看完整帮助
claude --help

# 查看版本信息
claude --version

# 查看 MCP 管理帮助
claude mcp --help

# 查看插件帮助
claude plugin --help

# 更新 Claude Code
claude update

# 健康检查
claude doctor
```

---

## 🔗 相关资源

- **官方网站**: https://claude.com/claude-code
- **GitHub Issues**: https://github.com/anthropics/claude-code/issues
- **文档**: 在 Claude Code 中使用 `/help` 命令

---

## 💡 实用技巧

### 1. 创建命令别名（Windows PowerShell）

在 PowerShell 配置文件中添加：

```powershell
# $PROFILE

# 快速继续
function cc { claude --continue }

# 使用 Opus 模型
function claude-opus { claude --model opus }

# 带调试的会话
function claude-debug { claude --debug }
```

### 2. 环境变量配置

在系统环境变量中设置：

```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:18100
ANTHROPIC_AUTH_TOKEN=your-token
```

### 3. 项目模板

为新项目创建 `.claude/` 模板：

```
.claude/
  ├── settings.local.json      # 项目特定设置
  ├── CLAUDE.md                # 项目文档
  └── commands/                # 自定义命令
      ├── build.md
      ├── test.md
      └── deploy.md
```

---

## 📝 备忘清单

### 最常用命令

```bash
claude              # 启动新会话
claude -c           # 继续上次会话
claude -r           # 恢复历史会话
claude --help       # 查看帮助
claude --version    # 查看版本
claude update       # 更新 Claude Code
```

### 会话管理

```bash
-c, --continue                      # 继续最近会话
-r, --resume [搜索词]               # 恢复会话
--fork-session                      # Fork 会话
--session-id <uuid>                 # 指定会话ID
```

### 模型和输出

```bash
--model <sonnet|opus|haiku>         # 选择模型
--output-format <text|json>         # 输出格式
--print                             # 非交互模式
```

### 调试

```bash
--debug [filter]                    # 启用调试
--verbose                           # 详细输出
--mcp-debug                         # MCP 调试
```

---

**最后更新**: 2025-12-08
**适用版本**: Claude Code 最新版本
**作者**: 为 ERP-p 项目定制