# GitHub Tools - Dify Plugin

[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-blue)](https://github.com/langgenius/dify)
[![Python](https://img.shields.io/badge/Python-3.12+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> GitHub integration tools for the Dify AI platform. Enables AI agents to search repositories, fetch README files, browse issues, and retrieve repository information directly.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration (Optional)](#configuration-optional)
- [Tools](#tools)
  - [1. Search Repositories](#1-search-repositories)
  - [2. Get README](#2-get-readme)
  - [3. List Issues](#3-list-issues)
  - [4. Get Repository Info](#4-get-repository-info)
- [Development Guide](#development-guide)
  - [Local Debugging](#local-debugging)
  - [Project Structure](#project-structure)
  - [Extending Tools](#extending-tools)
- [API Reference](#api-reference)
- [FAQ](#faq)
- [License](#license)

---

## Overview

This plugin is a **tool-type plugin** for the **Dify** platform. It wraps the [GitHub REST API](https://docs.github.com/en/rest) and provides the following capabilities to AI agents in Dify:

| Tool | Function | Use Case |
|------|----------|----------|
| 🔍 **Search Repositories** | Search GitHub repos by keywords, sort by stars/forks/updated | Finding open source projects, technology research |
| 📖 **Get README** | Fetch a repository's README content | Understanding project usage, installation, and setup |
| 📋 **List Issues** | Filter and list repository issues by state and labels | Project health assessment, finding tasks to solve |
| 📊 **Get Repository Info** | Get repository metadata and recent commits | Quick project overview, activity evaluation |

**Features:**

- **No API Key Required** — Works without a GitHub Token (limited to 60 requests/hour)
- **Optional Token** — Configure a GitHub Token to get up to 5,000 requests/hour
- **Bilingual Support** — UI and error messages support both English and Chinese
- **Lightweight** — Only depends on the `dify_plugin` SDK and `httpx` HTTP client

---

## Quick Start

### Prerequisites

- Python 3.12 or higher
- Dify platform (version >= 0.5.0)
- Optional: a [GitHub Token](https://github.com/settings/tokens) (to increase API rate limits)

### Installation

1. Clone this repository or download the source:

```bash
git clone https://github.com/Ziming6666/GitHub-Tools---Dify-.git
cd GitHub-Tools---Dify-
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. **Install via Dify Marketplace** (recommended)

   Search for `github_tools` in the Dify plugin marketplace and install with one click.

4. **Manual Installation**

   Upload the packaged `.difypkg` file through the Dify admin console's plugin management page.

### Configuration (Optional)

Configure a GitHub Token in the plugin settings for higher API rate limits:

1. Go to [GitHub Token Settings](https://github.com/settings/tokens) and generate a token (no permissions required for public read access)
2. In the Dify plugin management page, find GitHub Tools and enter your Token

> **Note:** The plugin works without a token, but is limited to 60 anonymous requests per hour.

---

## Tools

### 1. Search Repositories

Search public repositories on GitHub.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | ✅ | Search keywords |
| `sort` | enum | ❌ | Sort by: `stars` (default) / `forks` / `updated` |
| `limit` | integer | ❌ | Number of results (1-20, default 5) |

**Example Response:**

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

### 2. Get README

Fetch the raw Markdown content of a repository's README.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo` | string | ✅ | Full repository name: `owner/repo` (e.g. `langgenius/dify`) |
| `extract_code` | boolean | ❌ | Whether to extract code snippets (default `true`, feature in development) |

**Returned Content:**

- Raw Markdown text of the README (truncated at 15,000 characters if exceeded)
- Additional repository info (description, stars, language, topics, license)

---

### 3. List Issues

List issues from a GitHub repository, filterable by state and labels.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo` | string | ✅ | Full repository name: `owner/repo` |
| `state` | enum | ❌ | State: `open` (default) / `closed` / `all` |
| `labels` | string | ❌ | Filter by labels, comma-separated (e.g. `bug,enhancement`) |
| `limit` | integer | ❌ | Number of issues to return (1-50, default 10) |

> **Note:** Pull Requests are automatically filtered out from the results.

---

### 4. Get Repository Info

Get detailed repository metadata and recent commit history.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo` | string | ✅ | Full repository name: `owner/repo` |

**Returned Content:**

- Basic info: name, description, language, license, homepage
- Stats: ⭐ stars, 🍴 forks, 👀 watchers, open issues count
- Properties: default branch, archived status, fork status, size
- Timestamps: created at, last updated, last pushed
- Last 3 commit records

---

## Development Guide

### Local Debugging

1. Copy the environment template and configure it:

```bash
cp .env.example .env
```

2. Edit the `.env` file with your Dify remote debugging info:

```env
INSTALL_METHOD=remote
REMOTE_INSTALL_URL=debug-plugin.dify.dev:5003
REMOTE_INSTALL_KEY=your-debug-key-here
GITHUB_TOKEN=your_github_token_here  # Optional
```

3. Install development dependencies:

```bash
pip install -e .
```

4. Start debug mode:

```bash
python main.py
```

### Project Structure

```
dify-plugin-github/
├── __init__.py                 # Package marker
├── main.py                     # Plugin entry point
├── manifest.yaml               # Plugin manifest
├── pyproject.toml              # Python project config
├── requirements.txt            # Dependency list
├── .env.example                # Debug environment template
├── readme/
│   └── README_zh_Hans.md       # Chinese README
├── _assets/
│   └── icon.svg                # GitHub icon
├── provider/
│   ├── github.yaml             # Provider definition (credentials, tools)
│   └── github.py               # Credential validation logic
└── tools/
    ├── search_repos.yaml       # Search repos - definition
    ├── search_repos.py         # Search repos - implementation
    ├── get_readme.yaml         # Get README - definition
    ├── get_readme.py           # Get README - implementation
    ├── list_issues.yaml        # List issues - definition
    ├── list_issues.py          # List issues - implementation
    ├── get_repo_info.yaml      # Get repo info - definition
    └── get_repo_info.py        # Get repo info - implementation
```

### Extending Tools

To add a new GitHub tool, follow these steps:

1. **Create a tool definition file** `tools/your_tool.yaml` with parameters and descriptions
2. **Create a tool implementation file** `tools/your_tool.py`, extend the `Tool` base class and implement the `_invoke` method
3. **Register with the provider** by adding your YAML path to the `tools` list in `provider/github.yaml`

YAML definitions and Python implementations are linked by filename — the Dify Plugin SDK loads them automatically.

---

## API Reference

### GitHub Rate Limits

| Authentication | Requests per Hour | How to Get |
|----------------|-------------------|------------|
| Anonymous (no token) | 60 | No configuration needed |
| Authenticated (with token) | 5,000 | Generate in GitHub Settings |

For more details, see the [GitHub REST API rate limit documentation](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).

### Dify Plugin SDK

- `dify_plugin` SDK version: `>=0.5.0`
- Base classes: `Plugin`, `ToolProvider`, `Tool`
- Message types: `ToolInvokeMessage`

---

## FAQ

<details>
<summary><b>Q: Is a GitHub Token required to use this plugin?</b></summary>
No. The plugin works in anonymous mode with a rate limit of 60 requests per hour. Configuring a token increases the limit to 5,000 requests per hour.
</details>

<details>
<summary><b>Q: What permissions does the token need?</b></summary>
All tools in this plugin only read public data, so no specific permissions are required. A token generated in GitHub Settings works without any scopes selected.
</details>

<details>
<summary><b>Q: What should I do if I get a 403 error?</b></summary>
A 403 error usually means the rate limit has been exceeded (60 requests/hour for anonymous users) or the token is invalid. Configure a valid GitHub Token or wait for the rate limit to reset.
</details>

<details>
<summary><b>Q: How do I get the full repository name?</b></summary>
The full repository name follows the format <code>owner/repo</code>, for example <code>langgenius/dify</code>. When you visit a repository on GitHub, the URL path is <code>github.com/owner/repo</code>.
</details>

<details>
<summary><b>Q: Why doesn't the extract_code parameter work in get_readme?</b></summary>
The <code>extract_code</code> parameter is declared in the YAML definition but the code extraction feature has not been implemented yet. It will be added in a future release.
</details>

---

## License

[MIT License](LICENSE)

Copyright © 2025

---

**Built with [Dify](https://github.com/langgenius/dify)**
