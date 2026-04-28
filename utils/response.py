import asyncio
import random
from astrbot.core.message.components import BaseMessageComponent

from astrbot.api.event import AstrMessageEvent

from .messages import (
    build_blocked_user_message,
    build_not_in_allowed_user_list_message,
)


def get_user_acceptance_message(config: dict, user_id: str | int) -> str | None:
    """根据插件配置和用户 ID 返回拒绝消息或 None。"""
    if config.get("blocked_users_enabled", False) and user_id in config.get("blocked_users", []):
        return build_blocked_user_message()

    if config.get("allowed_users_enabled", False) and user_id not in config.get("allowed_users", []):
        return build_not_in_allowed_user_list_message()

    return None

def get_group_acceptance_message(config: dict, group_id: str | int) -> str | None:
    """根据插件配置和群 ID 返回拒绝消息或 None。"""
    if config.get("blocked_groups_enabled", False) and group_id in config.get("blocked_groups", []):
        return build_blocked_user_message()

    if config.get("allowed_groups_enabled", False) and group_id not in config.get("allowed_groups", []):
        return build_not_in_allowed_user_list_message()

    return None

async def simulate_response_delay(min_delay: float = 1.0, max_delay: float = 3.14) -> None:
    """模拟消息处理延迟。"""
    await asyncio.sleep(random.uniform(min_delay, max_delay))


async def delayed_plain_result(
    event: AstrMessageEvent,
    text: str,
    min_delay: float = 1.0,
    max_delay: float = 3.14,
):
    """延迟后返回 plain_result 响应。"""
    await simulate_response_delay(min_delay, max_delay)
    return event.plain_result(text)

async def delayed_chain_result(
    event: AstrMessageEvent,
    chain: list[BaseMessageComponent],
    min_delay: float = 1.0,
    max_delay: float = 3.14,
):
    """延迟后返回 chain_result 响应。"""
    await simulate_response_delay(min_delay, max_delay)
    return event.chain_result(chain)
