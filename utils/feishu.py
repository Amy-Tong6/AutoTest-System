# 飞书发送消息
import requests

class Feishu:
    @staticmethod
    def send_message(feishu_webhook:str,content: str):
        """发送飞书消息"""
        data = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        resp = requests.post(feishu_webhook, json=data)
        if resp.status_code != 200:
            raise Exception(f"❌ 飞书消息发送失败: {resp.text}")
        print("✅ 飞书消息发送成功")