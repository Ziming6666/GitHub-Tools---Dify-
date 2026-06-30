# GitHub Tools - Dify 插件

[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-blue)](https://github.com/langgenius/dify)
[![Python](https://img.shields.io/badge/Python-3.12+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> 为 Dify AI 应用平台提供 GitHub 集成工具，让 AI 助手能够直接搜索仓库、获取 README、浏览 Issue 和查看仓库信息。

---

## 📋 目录

- [功能概述](#功能概述)
- [快速开始](#快速开始)
  - [前提条件](#前提条件)
  - [安装插件](#安装插件)
  - [配置凭据（可选）](#配置凭据可选)
- [工具列表](#工具列表)
  - [1. 搜索仓库](#1-搜索仓库)
  - [2. 获取 README](#2-获取-readme)
  - [3. 列出 Issue](#3-列出-issue)
  - [4. 获取仓库信息](#4-获取仓库信息)
- [开发指南](#开发指南)
  - [本地调试](#本地调试)
  - [项目结构](#项目结构)
  - [扩展工具](#扩展工具)
- [API 参考](#api-参考)
- [常见问题](#常见问题)
- [许可](#许可)

---

## 功能概述

本插件是 **Dify** 平台的工具类插件，封装了 [GitHub REST API](https://docs.github.com/zh/rest)，为 Dify 中的 AI Agent 提供以下能力：

| 工具 | 功能 | 适用场景 |
|------|------|----------|
| 🔍 **搜索仓库** | 按关键词搜索 GitHub 仓库，支持按星标/ forks/ 更新时间排序 | 寻找开源项目、技术选型调研 |
| 📖 **获取 README** | 获取指定仓库的 README 文档内容 | 了解项目用途、安装和使用方式 |
| 📋 **列出 Issue** | 按状态和标签筛选仓库的 Issue 列表 | 项目健康度评估、寻找待解决任务 |
| 📊 **获取仓库信息** | 获取仓库元数据和最近提交记录 | 快速了解项目概况、活跃度评估 |

**特点：**

- **无需 API Key** — 无需 GitHub Token 即可使用（受限于 60 次/小时的匿名请求限额）
- **可选 Token** — 配置 GitHub Token 后可提升至 5000 次/小时
- **双语言支持** — 界面和错误提示同时支持中文和英文
- **轻量高效** — 仅依赖 `dify_plugin` SDK 和 `httpx` HTTP 客户端

---

## 快速开始

### 前提条件

- Python 3.12 或更高版本
- Dify 平台（版本 >= 0.5.0）
- 可选：一个 [GitHub Token](https://github.com/settings/tokens)（用于提升 API 速率限制）

### 安装插件

1. 克隆此仓库或下载源码包：

```bash
git clone https://github.com/Ziming6666/GitHub-Tools---Dify-.git
cd GitHub-Tools---Dify-
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. **通过 Dify 插件市场安装**（推荐）

   在 Dify 的插件市场中搜索 `github_tools` 并一键安装。

4. **手动安装**

   将打包后的插件 `.difypkg` 文件通过 Dify 管理后台的"插件管理"页面上传安装。

### 配置凭据（可选）

在插件设置中配置 GitHub Token 以获得更高的 API 请求限额：

1. 前往 [GitHub Token 设置页](https://github.com/settings/tokens) 生成一个 Token（无需任何权限即可公开读取）
2. 在 Dify 插件管理中找到 GitHub Tools，填入 Token

> **提示：** 不配置 Token 也能正常使用，仅受限于 60 次/小时的匿名请求限额。

---

## 工具列表

### 1. 搜索仓库

在 GitHub 上搜索公开仓库。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | 字符串 | ✅ | 搜索关键词 |
| `sort` | 枚举 | ❌ | 排序方式：`stars`（默认）/ `forks` / `updated` |
| `limit` | 整数 | ❌ | 返回数量（1-20，默认 5） |

**返回示例：**

```json
{
  "total_count": 2,
  "results": [
    {
      "name": "langgenius/dify",
      "description": "Dify is an open-source LLM application development platform",
      "stars": 58000,
      "forks": 8500,
      "language": "Python",
      "url": "https://github.com/langgenius/dify",
      "topics": ["llm", "ai", "chatbot"],
      "updated_at": "2025-06-26T10:00:00Z"
    }
  ],
  "summary": "Found 2 repositories.\n\n#### 1. [langgenius/dify](https://github.com/langgenius/dify)\n⭐ 58,000 · 🍴 8,500 · Python\nDify is an open-source LLM application development platform"
}
```

---

### 2. 获取 README

获取指定仓库的 README 文档原始 Markdown 内容。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `repo` | 字符串 | ✅ | 仓库全名，格式：`owner/repo`（如 `langgenius/dify`） |
| `extract_code` | 布尔 | ❌ | 是否提取代码片段（默认 `true`，此功能尚在开发中） |

**返回内容：**

- README 的原始 Markdown 文本（超过 15,000 字符时自动截断）
- 辅助仓库信息（描述、星标数、语言、主题标签、许可证）

---

### 3. 列出 Issue

列出指定仓库的 Issue 列表，可按状态和标签筛选。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `repo` | 字符串 | ✅ | 仓库全名，格式：`owner/repo` |
| `state` | 枚举 | ❌ | 状态：`open`（默认）/ `closed` / `all` |
| `labels` | 字符串 | ❌ | 标签过滤，多个标签用逗号分隔（如 `bug,enhancement`） |
| `limit` | 整数 | ❌ | 返回数量（1-50，默认 10） |

> **注意：** Pull Request 会被自动过滤，不包含在返回结果中。

---

### 4. 获取仓库信息

获取仓库的详细元数据及最近的提交记录。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `repo` | 字符串 | ✅ | 仓库全名，格式：`owner/repo` |

**返回内容：**

- 基本信息：名称、描述、语言、许可证、主页
- 统计数据：⭐ 星标数、🍴 Fork 数、👀 关注数、开放 Issue 数
- 仓库属性：默认分支、是否归档、是否为 Fork、仓库大小
- 时间信息：创建时间、最后更新、最后推送
- 最近 3 条提交记录

---

## 开发指南

### 本地调试

1. 复制环境变量模板并配置：

```bash
cp .env.example .env
```

2. 编辑 `.env` 文件填入 Dify 远程调试信息：

```env
INSTALL_METHOD=remote
REMOTE_INSTALL_URL=debug-plugin.dify.dev:5003
REMOTE_INSTALL_KEY=your-debug-key-here
GITHUB_TOKEN=your_github_token_here  # 可选
```

3. 安装开发依赖：

```bash
pip install -e .
```

4. 启动调试模式：

```bash
python main.py
```

### 项目结构

```
dify-plugin-github/
├── __init__.py                 # 包标记
├── main.py                     # 插件入口
├── manifest.yaml               # 插件清单
├── pyproject.toml              # Python 项目配置
├── requirements.txt            # 依赖列表
├── .env.example                # 调试环境模板
├── _assets/
│   └── icon.svg                # GitHub 图标
├── provider/
│   ├── github.yaml             # 提供者定义（凭据、工具列表）
│   └── github.py               # 凭据校验逻辑
└── tools/
    ├── search_repos.yaml       # 搜索仓库 - 定义文件
    ├── search_repos.py         # 搜索仓库 - 实现
    ├── get_readme.yaml         # 获取 README - 定义文件
    ├── get_readme.py           # 获取 README - 实现
    ├── list_issues.yaml        # 列出 Issue - 定义文件
    ├── list_issues.py          # 列出 Issue - 实现
    ├── get_repo_info.yaml      # 获取仓库信息 - 定义文件
    └── get_repo_info.py        # 获取仓库信息 - 实现
```

### 扩展工具

要添加新的 GitHub 工具，请遵循以下步骤：

1. **创建工具定义文件** `tools/your_tool.yaml`，声明参数和描述
2. **创建工具实现文件** `tools/your_tool.py`，继承 `Tool` 基类并实现 `_invoke` 方法
3. **注册到提供者**：在 `provider/github.yaml` 的 `tools` 列表中添加你的 YAML 路径

YAML 定义和 Python 实现之间通过文件名关联，Dify 插件 SDK 会自动加载。

---

## API 参考

### GitHub 速率限制

| 认证方式 | 每小时请求数 | 获取方式 |
|----------|-------------|----------|
| 匿名（无 Token） | 60 | 无需配置 |
| 已认证（有 Token） | 5,000 | 在 GitHub Settings 生成 |

更多详情请参考 [GitHub REST API 速率限制文档](https://docs.github.com/zh/rest/using-the-rest-api/rate-limits-for-the-rest-api)。

### Dify 插件 SDK

- `dify_plugin` SDK 版本：`>=0.5.0`
- 基类：`Plugin`, `ToolProvider`, `Tool`
- 消息类型：`ToolInvokeMessage`

## 常见问题

<details>
<summary><b>问：必须配置 GitHub Token 才能使用吗？</b></summary>
不需要。匿名模式下可以正常使用，但速率限制为 60 次/小时。推荐配置 Token 以获得 5000 次/小时的限额。
</details>

<details>
<summary><b>问：Token 需要哪些权限？</b></summary>
本插件的所有工具仅读取公开数据，不需要任何特定权限。在 GitHub Settings 生成的 Token 无需勾选任何 scope 即可使用。
</details>

<details>
<summary><b>问：提示 403 错误怎么办？</b></summary>
403 错误通常意味着速率限制已用完（匿名用户 60 次/小时），或 Token 无效。建议配置有效的 GitHub Token 或等待速率限制重置。
</details>

<details>
<summary><b>问：如何获取仓库的完整名称？</b></summary>
仓库完整名称的格式为 <code>owner/repo</code>，例如 <code>langgenius/dify</code>。在 GitHub 上访问仓库时，URL 路径即为 <code>github.com/owner/repo</code>。
</details>

<details>
<summary><b>问：extract_code 参数在 get_readme 中不起作用？</b></summary>
当前版本中 <code>extract_code</code> 参数已在 YAML 定义中声明，但相应的代码提取功能尚未实现，会在后续版本中添加。
</details>

---

## 许可

[MIT License](LICENSE)

版权所有 © 2025

---

**使用 [Dify](https://github.com/langgenius/dify) 平台构建**
