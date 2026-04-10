import allure
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

# ==============================================
# 🔥 内置钩子可以监听用例结果
# tryfirst:优先执行
# hookwrapper: 包裹测试用例执行
# ==============================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()

    # 用例执行失败
    if report.when == "call" and report.failed:
        try:
            # 安全获取 page
            runner = item.funcargs.get("web_runner")
            allure.attach(
                runner.screenshot(),
                name="失败截图",
                attachment_type=allure.attachment_type.PNG
            )
        except Exception as e:
            print(f"截图失败: {e}")