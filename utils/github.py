# 发布到GitHub Pages
import os
from pathlib import Path
import requests
import yaml
import shutil
import subprocess
import time

BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"

class Github:
    def __init__(self, customer_id: str, file_path: Path):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            customers = yaml.safe_load(f)["customers"]

        if customer_id not in customers:
            raise Exception(f"客户 {customer_id} 未配置")

        customer = customers[customer_id]

        self.local_repo = customer["local_repo"]
        self.url = f"https://{customer["user_name"]}.github.io/{customer["repo_name"]}/{self.file_name}"

    def _update_local(self):
        """拉取最新代码"""
        print("🚀 更新本地仓库代码")
        os.chdir(self.local_repo)
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        shutil.copy(self.file_path, self.file_name)  # 复制且不改名

    def _push_to_remote(self):
        """推送到GitHub Pages"""
        print("🚀 推送到GitHub Pages")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"auto publish {self.file_name}"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)

    def _wait_for_page_ready(self, timeout=300, interval=30):
        print(f"⏳ 等待 GitHub Pages 部署完成：{self.url}")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                time.sleep(interval)
                response = requests.get(
                    self.url,
                    headers={"Cache-Control": "no-cache"},
                    timeout=10
                )
                if response.status_code == 200:
                    print("✅ 页面已部署完成！")
                    return True
                elif response.status_code == 404:
                    print(f"🔄 页面部署中... {interval}秒后重试")
            except Exception as e:
                print(f"⚠️ 检查失败：{str(e)}")

        print(f"❌ 页面部署超时：{self.url}")
        return False

    def publish_file(self):
        """上传单个文件 到 GitHub Pages"""
        self._update_local()
        self._push_to_remote()
        self._wait_for_page_ready()
        return self.url