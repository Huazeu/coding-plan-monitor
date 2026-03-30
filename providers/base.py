"""Provider 基类 - 定义统一接口"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class UsageResult:
    provider: str
    account_name: str
    model_usage: int
    tool_usage: int
    tokens_percentage: int
    mcp_percentage: int
    chart_data: list
    updated_at: str
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "account": self.account_name,
            "model_usage": self.model_usage,
            "tool_usage": self.tool_usage,
            "tokens_percentage": self.tokens_percentage,
            "mcp_percentage": self.mcp_percentage,
            "chart_data": self.chart_data,
            "updated_at": self.updated_at,
            "error": self.error,
        }


class BaseProvider(ABC):
    """所有 Provider 必须实现的抽象基类"""

    name: str = "base"
    display_name: str = "Base Provider"

    @abstractmethod
    def query(self, token: str, time_range: str = "today", **kwargs) -> UsageResult:
        """
        查询用量

        Args:
            token: 认证令牌
            time_range: 时间范围 (today/week/month)
            **kwargs: 其他参数

        Returns:
            UsageResult: 查询结果
        """
        pass

    @abstractmethod
    def validate_token(self, token: str) -> bool:
        """
        验证 token 是否有效

        Args:
            token: 认证令牌

        Returns:
            bool: 是否有效
        """
        pass

    def get_display_name(self) -> str:
        return self.display_name
