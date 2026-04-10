import os
import shutil
import pytest
import subprocess
from pathlib import Path
from datetime import datetime
from notify.github import Github
from notify.feishu import Feishu

BASE_DIR = Path(__file__).parents[2] # AutoTest-System

def run(customer_id: str):
    # 1. 运行测试，生成 allure json 结果
    print("🚀 开始执行测试...")
    allure_results_dir = BASE_DIR / "allure-results"
    pytest.main([
        "--alluredir", str(allure_results_dir),  # ✔️ 强制指定根目录
        "-vs"
    ])

    # 2. 准备报告目录
    print("📃 准备报告文件夹")
    report_dir = BASE_DIR / "allure-reports" / customer_id
    os.makedirs(report_dir, exist_ok=True)  # 已经存在不报错

    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    report_path = report_dir / f"{timestamp}.html"
    tmp_report_dir = report_dir / f"{timestamp}_tmp"  # 原始报告的文件夹


    # 3. 生成原始报告
    print("\n📊 生成报告中...")
    subprocess.run([
        "allure", "generate",
        str(allure_results_dir),
        "-o",
        str(tmp_report_dir),
        "--clean"
    ], check=True)

    # 4. 生成最终报告
    subprocess.run([
        "allure-combine",
        str(tmp_report_dir),
        "--dest", str(report_dir)
    ], check=True)

    # 5. 重命名为带时间戳的文件名
    os.rename(report_dir / "complete.html", report_path)

    # 6. 清理临时目录
    print("\n🧹 清理临时文件...")
    shutil.rmtree(tmp_report_dir)

    # 7. 推送到GitHub + 等待部署
    print("📤 发布到GitHub...")
    report_url = Github(customer_id, report_path).publish_file()

    # 8.飞书消息：@所有人 + 报告链接
    Feishu.send_message(
        f"<at user_id=\"all\"></at>\n🚀 测试报告已出炉！各位大佬请检阅～ 🙏\n{report_url}"
    )
    print(f"🌍 访问链接：{report_url}")

if __name__ == "__main__":
    run("github")