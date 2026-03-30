"""智谱 GLM Coding Plan Provider"""

import re
from datetime import datetime
from typing import Optional

import requests

from .base import BaseProvider, UsageResult


class GLMProvider(BaseProvider):
    name = "glm"
    display_name = "智谱 GLM"

    def __init__(self):
        self.base_url = "https://open.bigmodel.cn"

    def validate_token(self, token: str) -> bool:
        if not token:
            return False
        if token.startswith("Bearer "):
            token = token[7:]
        return len(token) > 10

    def query(self, token: str, time_range: str = "today", **kwargs) -> UsageResult:
        if token.startswith("Bearer "):
            token = token[7:]

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            model_data = self._fetch_model_usage(headers, time_range)
            tool_data = self._fetch_tool_usage(headers, time_range)
            quota_data = self._fetch_quota(headers)

            chart_data = self._build_chart_data(model_data, tool_data, time_range)

            return UsageResult(
                provider=self.name,
                account_name=kwargs.get("account_name", "默认账号"),
                model_usage=model_data.get("total", 0),
                tool_usage=tool_data.get("total", 0),
                tokens_percentage=quota_data.get("tokens_percentage", 0),
                mcp_percentage=quota_data.get("mcp_percentage", 0),
                chart_data=chart_data,
                updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        except Exception as e:
            return UsageResult(
                provider=self.name,
                account_name=kwargs.get("account_name", "默认账号"),
                model_usage=0,
                tool_usage=0,
                tokens_percentage=0,
                mcp_percentage=0,
                chart_data=[],
                updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                error=str(e),
            )

    def _fetch_model_usage(self, headers: dict, time_range: str) -> dict:
        url = f"{self.base_url}/api/monitor/usage/model-usage"
        params = {"time_range": time_range}
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("data", {}).get("items", [])
        total = sum(item.get("token_usage", 0) for item in items)

        return {"total": total, "items": items}

    def _fetch_tool_usage(self, headers: dict, time_range: str) -> dict:
        url = f"{self.base_url}/api/monitor/usage/tool-usage"
        params = {"time_range": time_range}
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("data", {}).get("items", [])
        total = 0
        for item in items:
            total += item.get("totalNetworkSearchCount", 0)
            total += item.get("totalWebReadMcpCount", 0)
            total += item.get("totalGithubMcpCount", 0)
            total += item.get("totalSearchMcpCount", 0)

        return {"total": total, "items": items}

    def _fetch_quota(self, headers: dict) -> dict:
        url = f"{self.base_url}/api/monitor/usage/quota/limit"
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        quota = data.get("data", {})

        tokens_5h_limit = quota.get("tokens_5h_limit", 0)
        tokens_5h_used = quota.get("tokens_5h_used", 0)
        mcp_limit = quota.get("mcp_tool_monthly_limit", 0)
        mcp_used = quota.get("mcp_tool_monthly_used", 0)

        tokens_pct = int(tokens_5h_used / tokens_5h_limit * 100) if tokens_5h_limit > 0 else 0
        mcp_pct = int(mcp_used / mcp_limit * 100) if mcp_limit > 0 else 0

        return {
            "tokens_percentage": min(tokens_pct, 100),
            "mcp_percentage": min(mcp_pct, 100),
        }

    def _build_chart_data(self, model_data: dict, tool_data: dict, time_range: str) -> list:
        items = model_data.get("items", [])
        chart_data = []
        for item in items:
            timestamp = item.get("timestamp", "")
            date_str = self._format_timestamp(timestamp, time_range)
            chart_data.append({
                "time": date_str,
                "tokens": item.get("token_usage", 0),
            })
        return chart_data

    def _format_timestamp(self, timestamp: str, time_range: str) -> str:
        try:
            if time_range == "today":
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                return dt.strftime("%H:%M")
            else:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                return dt.strftime("%m-%d")
        except Exception:
            return timestamp[:10] if len(timestamp) >= 10 else timestamp
