import os
import shutil
import pytest
import subprocess
from dotenv import load_dotenv

load_dotenv()
PORT = int(os.getenv("PORT", 8888))
REPORT_URL = f"http://127.0.0.1:{PORT}/index.html"

def run():
    print("🚀 开始执行测试...")

    # 1. 运行测试，生成 allure json 结果
    pytest.main(["--alluredir=allure-results", "-vs"])

    # 2. 生成 HTML 报告
    print("\n📊 生成 HTML 报告...")
    subprocess.run([
        "allure",
        "generate",
        "allure-results",
        "-o",
        "allure-report-tmp",
        "--clean"
    ])
    print("✅ 报告已生成！")

    # 3. 更新正式报告
    print("\n🚀 更新正式报告...")
    if not os.path.exists("allure-report"):
        shutil.copytree("allure-report-tmp", "allure-report")
    else:
        # 覆盖正式报告html
        if os.path.exists("allure-report-tmp"):
            shutil.copy("allure-report-tmp/index.html", "allure-report/index.html")

        # 复制报告数据文件夹
        if os.path.exists("allure-report/data"):
            shutil.rmtree("allure-report/data")
            shutil.copytree("allure-report-tmp/data", "allure-report/data")
    print(f"✅ 报告已更新！{REPORT_URL}")

    return
    # 4.发送飞书消息
    from notify.feishu import send_report
    send_report(REPORT_URL)

if __name__ == "__main__":
    run()
