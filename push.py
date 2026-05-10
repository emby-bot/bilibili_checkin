import os
import requests
from datetime import datetime, timedelta, timezone
from loguru import logger


def format_push_message(all_results):
    content = ["📣 Bilibili 任务报告\n"]

    for result in all_results:
        user_info = result.get('user_info')

        if user_info:
            account_name = user_info['uname']
            level = user_info['level_info']['current_level']
            content.append("━━━━━━━━━━━━━━")
            content.append(f"账号：{account_name}  Lv.{level}")
        else:
            account_name = f"账号 {result['account_index']}"
            content.append("━━━━━━━━━━━━━━")
            content.append(account_name)

        for name, (success, message) in result['tasks'].items():
            status_icon = "✅" if success else "❌"
            reason = f" - {message}" if message else ""
            content.append(f"{status_icon} {name}{reason}")

        if user_info:
            content.append(f"💰 硬币余额：{user_info['money']}")

    beijing_time = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
    content.append(f"\n🕐 报告时间：{beijing_time}")

    return "\n".join(content)


def send_to_telegram(bot_token, chat_id, title, content):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    text = f"{title}\n\n{content}" if title else content

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

        logger.error(f"Telegram 推送失败: {result}")
        return False

    except Exception as e:
        logger.error(f"Telegram 推送异常: {e}")
        return False


def send_to_bark(bark_key, title, content, group=None, icon=None):
    """
    Bark 推送。

    支持两种 BARK_KEY 写法：

    1. 完整地址：
       BARK_KEY=https://api.day.app/你的Key

    2. 只填 Key：
       BARK_KEY=你的Key
    """
    bark_key = (bark_key or "").strip()
    if not bark_key:
        logger.info("未配置 BARK_KEY，跳过 Bark 推送")
        return False

    if bark_key.startswith("http://") or bark_key.startswith("https://"):
        url = bark_key.rstrip("/")
    else:
        url = f"https://api.day.app/{bark_key}"

    data = {
        "title": title or "Bilibili 任务报告",
        "body": content,
    }

    if group:
        data["group"] = group

    if icon:
        data["icon"] = icon

    try:
        res = requests.post(url, json=data, timeout=20)
        result = res.json()

        # Bark 一般返回 code=200 表示成功
        if result.get("code") == 200 or result.get("message") == "success":
            logger.info("Bark 推送成功！")
            return True

        logger.error(f"Bark 推送失败: {result}")
        return False

    except Exception as e:
        logger.error(f"Bark 推送异常: {e}")
        return False
