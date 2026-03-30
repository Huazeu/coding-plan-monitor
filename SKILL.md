---
name: coding-plan-monitor
description: |
  查询各大 AI 平台的 Coding Plan 用量配额。当用户询问：
  - GLM/智谱/扣子/Kimi 用量/配额/余额
  - 今天/本周/本月使用了多少 tokens
  - Coding Plan 状态/剩余量
  - 某个账号的用量情况

  注意：需要用户提供对应的 Bearer Token 才能查询。
---

# Coding Plan Monitor

小龙虾的 Coding Plan 用量监控工具，支持查询多个 AI 平台的用量情况。

## 支持平台

- ✅ **智谱 GLM** (open.bigmodel.cn)
- 🔲 扣子 Coze (规划中)
- 🔲 月之暗面 Kimi (规划中)
- 🔲 阿里通义千问 (规划中)

## 使用前提

### 1. 安装依赖

```bash
pip install requests pyyaml
```

### 2. 获取 Token

**智谱 GLM Token 获取方式：**
1. 登录智谱开放平台 (https://open.bigmodel.cn)
2. 打开浏览器开发者工具 (F12)
3. 切换到 Network 标签
4. 进入 Coding Plan 页面
5. 找到任意请求，复制 Authorization header 中的 Bearer Token

### 3. 配置 Token

设置环境变量：
```bash
export GLM_TOKEN="Bearer 你的Token"
```

或在命令行直接传入：
```bash
python main.py glm --token "Bearer 你的Token"
```

## 使用方法

### 查询所有已配置平台

```bash
python main.py
```

### 查询指定平台

```bash
python main.py glm
```

### 指定时间范围

```bash
python main.py glm --time-range today    # 当日
python main.py glm --time-range week     # 最近7天
python main.py glm --time-range month    # 本月
```

### JSON 格式输出

```bash
python main.py glm --json
```

## 输出示例

```
╔══════════════════════════════════════════════════════════╗
║              智谱 GLM Coding Plan                        ║
╠══════════════════════════════════════════════════════════╣
║  📊 模型用量 (Tokens):  1,234,567                      ║
║  🔧 工具调用次数:       89                               ║
╠══════════════════════════════════════════════════════════╣
║  ⏱️  5小时 Tokens 配额:  ████████░░░░░░░░  45%       ║
║  📅 本月 MCP 工具配额:   ███░░░░░░░░░░░░░░  12%       ║
╚══════════════════════════════════════════════════════════╝
更新时间: 2026-03-30 12:00:00
```

## 添加新平台

参考 `providers/base.py` 实现新的 Provider：

```python
from .base import BaseProvider, UsageResult

class MyProvider(BaseProvider):
    name = "myplatform"
    display_name = "我的平台"

    def validate_token(self, token: str) -> bool:
        # 验证 token 格式
        pass

    def query(self, token: str, time_range: str = "today", **kwargs) -> UsageResult:
        # 调用 API 获取用量
        pass
```

然后在 `providers/__init__.py` 中注册即可。

## 定时任务 (Linux/macOS)

```bash
# 添加定时任务
(crontab -l 2>/dev/null; echo "*/10 * * * * cd /path/to/coding-plan-monitor && python main.py glm >> /var/log/coding-plan.log") | crontab -
```

## 定时任务 (Windows)

使用任务计划程序或创建批处理文件 `query.bat`：

```bat
@echo off
cd /d %~dp0
python main.py glm
pause
```

然后添加到任务计划程序，设置每 10 分钟运行一次。
