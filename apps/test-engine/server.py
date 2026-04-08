# 启动报告静态服务
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from dotenv import load_dotenv

load_dotenv()
PORT = int(os.getenv("REPORT_SERVER_PORT"))
REPORT_URL = int(os.getenv("REPORT_SERVER_URL"))

def start_static_server():
    # 确保报告文件夹存在
    os.makedirs("allure-report", exist_ok=True)
    os.chdir("allure-report")

    # 启动静态服务
    # 0.0.0.0 表示本机/局域网都能访问
    server = HTTPServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler)
    print(f"🌍 服务已启动-访问地址：{REPORT_URL}")

    # 永久运行服务
    server.serve_forever()

if __name__ == "__main__":
    start_static_server()