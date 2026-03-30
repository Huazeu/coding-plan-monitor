"""Coding Plan Monitor - 多平台 Coding Plan 用量查询工具"""

import argparse
import json
import os
import sys

try:
    import yaml
except ImportError:
    yaml = None

from providers import PROVIDERS


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    if not os.path.exists(config_path):
        return {}
    if yaml is None:
        print("⚠ 需要 PyYAML: pip install pyyaml")
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def format_bar(percentage: int, width: int = 20) -> str:
    filled = int(width * percentage / 100)
    empty = width - filled
    return "█" * filled + "░" * empty


def print_result(result):
    if result.error:
        print(f"\n❌ {result.provider.upper()} - {result.account_name}: {result.error}\n")
        return

    width = 56
    print()
    print("╔" + "═" * width + "╗")
    title = f"{result.provider.upper()} Coding Plan"
    print("║" + title.center(width) + "║")
    print("╠" + "═" * width + "╣")
    print(f"║  📊 模型用量 (Tokens):  {result.model_usage:>15,}              ║")
    print(f"║  🔧 工具调用次数:       {result.tool_usage:>15,}              ║")
    print("╠" + "═" * width + "╣")
    bar1 = format_bar(result.tokens_percentage)
    print(f"║  ⏱️  5小时 Tokens 配额:  {bar1}  {result.tokens_percentage:>3}%       ║")
    bar2 = format_bar(result.mcp_percentage)
    print(f"║  📅 本月 MCP 工具配额:   {bar2}  {result.mcp_percentage:>3}%       ║")
    print("╚" + "═" * width + "╝")
    print(f"  更新时间: {result.updated_at}")
    print()


def print_json(result):
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


def query_provider(provider_name: str, token: str, time_range: str, account_name: str = "默认账号", as_json: bool = False):
    if provider_name not in PROVIDERS:
        print(f"❌ 不支持的平台: {provider_name}")
        print(f"   支持的平台: {', '.join(PROVIDERS.keys())}")
        return

    provider = PROVIDERS[provider_name]()
    result = provider.query(token, time_range, account_name=account_name)

    if as_json:
        print_json(result)
    else:
        print_result(result)


def main():
    parser = argparse.ArgumentParser(
        description="Coding Plan Monitor - 多平台 Coding Plan 用量查询",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "provider",
        nargs="?",
        default=None,
        help=f"平台名称 ({', '.join(PROVIDERS.keys())})，不指定则查询所有已配置平台",
    )
    parser.add_argument("--token", "-t", help="认证 Token (也可通过环境变量设置)")
    parser.add_argument("--time-range", "-r", default="today", choices=["today", "week", "month"], help="时间范围 (默认: today)")
    parser.add_argument("--account", "-a", help="账号名称 (多账号时指定)")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()
    config = load_config()

    if args.provider:
        provider_name = args.provider.lower()
        token = args.token or os.environ.get(f"{provider_name.upper()}_TOKEN", "")

        if not token and provider_name in config:
            accounts = config[provider_name].get("accounts", [])
            if accounts:
                account = accounts[0]
                token = os.path.expandvars(account.get("token", ""))
                account_name = args.account or account.get("name", "默认账号")
            else:
                account_name = args.account or "默认账号"
        else:
            account_name = args.account or "默认账号"

        if not token:
            print(f"❌ 未提供 {provider_name} 的 Token")
            print(f"   方式1: 设置环境变量 {provider_name.upper()}_TOKEN")
            print(f"   方式2: 命令行传入 --token")
            print(f"   方式3: 在 config.yaml 中配置")
            sys.exit(1)

        query_provider(provider_name, token, args.time_range, account_name, args.json)
    else:
        if not config:
            print("❌ 未指定平台且无配置文件 (config.yaml)")
            print(f"   用法: python main.py <{'|'.join(PROVIDERS.keys())}>")
            sys.exit(1)

        found = False
        for provider_name, provider_config in config.items():
            if provider_name not in PROVIDERS:
                continue
            if provider_config.get("enabled") is False:
                continue

            accounts = provider_config.get("accounts", [])
            if not accounts:
                token = os.path.expandvars(provider_config.get("token", ""))
                if token:
                    query_provider(provider_name, token, args.time_range, "默认账号", args.json)
                    found = True
            else:
                for account in accounts:
                    token = os.path.expandvars(account.get("token", ""))
                    if token:
                        name = account.get("name", "默认账号")
                        query_provider(provider_name, token, args.time_range, name, args.json)
                        found = True

        if not found:
            print("❌ 配置文件中没有可用的 Token")
            sys.exit(1)


if __name__ == "__main__":
    main()
