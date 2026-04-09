# 飞书发送消息
import requests
import os
from dotenv import load_dotenv

load_dotenv()
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK")

def send(payload):
    res=requests.post(FEISHU_WEBHOOK, json=payload)
    if res.status_code==200:
        print("👌 发送飞书成功")
    else:
        print(f"❌ 发送飞书失败：{res.text.msg}")

def send_report(report_url):
    payload = {
        "msg_type": "interactive",
        "card": {
            "schema": "2.0",
            "config": {
                "update_multi": True,
                "style": {
                    "text_size": {
                        "normal_v2": {
                            "default": "normal",
                            "pc": "normal",
                            "mobile": "heading"
                        }
                    }
                }
            },
            "body": {
                "direction": "vertical",
                "padding": "12px 12px 12px 12px",
                "elements": [
                    {
                        "tag": "markdown",
                        "content": "<at id=all></at>\n🚀 自动化测试报告已生成\n🔥 请点击下方按钮查看详细报告",
                        "text_align": "left",
                        "text_size": "normal_v2",
                        "margin": "0px 0px 0px 0px"
                    },
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "👀 详细报告"
                        },
                        "type": "default",
                        "width": "default",
                        "size": "medium",
                        "behaviors": [
                            {
                                "type": "open_url",
                                "default_url": report_url,
                                "pc_url": "",
                                "ios_url": "",
                                "android_url": ""
                            }
                        ],
                        "margin": "0px 0px 0px 0px"
                    }
                ]
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "测试报告已生成"
                },
                "subtitle": {
                    "tag": "plain_text",
                    "content": ""
                },
                "template": "blue",
                "padding": "10px 10px 10px 10px"
            }
        }
    }
    send(payload)

