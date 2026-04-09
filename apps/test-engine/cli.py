import os
import shutil
import pytest
import subprocess
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
PORT = int(os.getenv("PORT", 8888))
REPORT_URL = f"http://127.0.0.1:{PORT}/index.html"

def run(customer_id: str):
    # 1. 运行测试，生成 allure json 结果
    print("🚀 开始执行测试...")
    pytest.main(["--alluredir=allure-results", "-vs"])

    # 2. 准备报告目录
    print("📃 准备报告文件夹")
    report_dir = f"allure-reports/{customer_id}"
    os.makedirs(report_dir, exist_ok=True)  # 已经存在不报错
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    tmp_report_dir = f"{report_dir}/{timestamp}_tmp"  # report 生成目录
    final_html = f"{report_dir}/{timestamp}.html"  # 最终报告路径

    # 3. 生成原始报告
    print("\n📊 生成报告中...")
    subprocess.run([
        "allure", "generate",
        "allure-results",
        "-o",
        tmp_report_dir,
        "--clean"
    ], check=True)

    # 4. 生成最终报告
    subprocess.run([
        "allure-combine",
        tmp_report_dir,
        "--dest", report_dir
    ], check=True)

    # 重命名为带时间戳的文件名
    generated_html = f"{report_dir}/complete.html"
    os.rename(generated_html, final_html)

    # 清理临时目录
    print("\n🧹 清理临时文件...")
    shutil.rmtree(tmp_report_dir)
    shutil.rmtree("allure-results")

    # 5.发送飞书消息
    report_url = f"http://127.0.0.1:{PORT}/{final_html}"
    print(f"✅ 报告已生成！{report_url}")

    # from notify.feishu import send_report
    # send_report(REPORT_URL)

if __name__ == "__main__":
    run("dianping")