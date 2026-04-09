import pytest
from web_runner import WebRunner

# ==============================================
# 🔥 只给 WEB 用例使用
# ==============================================
@pytest.fixture(scope="module")
def web_runner():
    # 前置：只有 Web 用例引用时才会打开浏览器
    print("\n🚀 打开浏览器（module 级别）")
    runner = WebRunner()

    yield runner  # 提供给测试用例

    # 后置：当前客户所有用例跑完关闭
    print("\n🏁 关闭浏览器")
    runner.close()