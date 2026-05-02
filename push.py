import os
import requests
from datetime import datetime, timedelta, timezone
from loguru import logger


def format_push_message(all_results):
    content = ["📣 Bilibili 任务报告\n"]

    for result in all_results:
        user_info = result.get("user_info")

        if user_info:
            account_name = user_info["uname"]
            level = user_info["level_info"]["current_level"]
            content.append(f"━━━━━━━━━━━━━━")
            content.append(f"账号：{account_name}  Lv.{level}")
        else:
            account_name = f"账号 {result['account_index']}"
            content.append(f"━━━━━━━━━━━━━━")
            content.append(account_name)

        for name, (success, message) in result["tasks"].items():
            status_icon = "✅" if success else "❌"
            reason = f" - {message}" if message else ""
            content.append(f"{status_icon} {name}{reason}")

        if user_info:
            content.append(f"💰 硬币余额：{user_info['money']}")

    beijing_time = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    content.append(f"\n🕐 报告时间：{beijing_time}")

    return "\n".join(content)


def send_to_telegram(bot_token, chat_id, title, content):
    """
    发送 Telegram 通知
    """
    if not bot_token:
        logger.error("Telegram 推送失败：未配置 TG_BOT_TOKEN")
        return False

    if not chat_id:
        logger.error("Telegram 推送失败：未配置 TG_CHAT_ID")
        return False

    text = f"{title}\n\n{content}" if title else content

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }

    try:
        res = requests.post(url, data=data, timeout=20)
        result = res.json()

        if result.get("ok"):
            logger.info("Telegram 推送成功！")
            return True

        logger.error(f"Telegram 推送失败：{result}")
        return False

    except Exception as e:
        logger.error(f"Telegram 推送异常：{e}")
        return False


def send_to_pushplus(token, title, content):
    """
    兼容原来的 PushPlus 调用方式。

    原来 main.py 如果还是这样调用：
        send_to_pushplus(PUSHPLUS_TOKEN, title, content)

    现在 token 会被当成 Telegram Bot Token 使用。
    TG_CHAT_ID 从环境变量读取。
    """

    bot_token = (
        os.getenv("TG_BOT_TOKEN")
        or os.getenv("TELEGRAM_BOT_TOKEN")
        or token
    )

    chat_id = (
        os.getenv("TG_CHAT_ID")
        or os.getenv("TELEGRAM_CHAT_ID")
    )

    return send_to_telegram(bot_token, chat_id, title, content)
