# 飞书发送消息
import requests
import os
from dotenv import load_dotenv

load_dotenv()
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK")

class Feishu:
    @staticmethod
    def send_message(content: str):
        """发送飞书消息"""
        data = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        resp = requests.post(FEISHU_WEBHOOK, json=data)
        if resp.status_code != 200:
            raise Exception(f"❌ 飞书消息发送失败: {resp.text}")
        print("✅ 飞书消息发送成功")