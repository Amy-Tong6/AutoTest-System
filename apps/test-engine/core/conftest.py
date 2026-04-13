import allure
import pytest
from web_runner import WebRunner
from api_runner import ApiRunner
import json
# ==============================================
# 🔥 只给 WEB 用例使用
# ==============================================
@pytest.fixture(scope="module")
def web_runner():
    # 前置：
    print("\n🚀 开始运行 Web Runner")
    runner = WebRunner()

    yield runner  # 提供给测试用例

    # 后置：
    print("\n🏁 关闭浏览器")
    runner.close()

# ==============================================
# 🔥 只给 API 用例使用
# ==============================================
@pytest.fixture(scope="module")
def api_runner():
    # 前置：
    print("\n🚀 开始运行 API Runner")
    runner = ApiRunner()

    yield runner  # 提供给测试用例

    # 后置：
    print("\n🏁 关闭")
    runner.close()


# ==============================================
# 🔥 内置钩子可以监听用例结果
# tryfirst:优先执行
# hookwrapper: 包裹测试用例执行
# ==============================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call): # call 缺少会不执行
    outcome = yield
    report = outcome.get_result()

    # 用例执行失败
    if report.when == "call" and report.failed:
        # 1. Web UI 自动化：失败截图
        if "web_runner" in item.funcargs:
            try:
                web_runner = item.funcargs.get("web_runner")
                allure.attach(
                    web_runner.screenshot(),
                    name="失败截图",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                print(f"Web截图失败: {e}")

        # 2. API 接口自动化：失败展示 请求 + 响应
        if "api_runner" in item.funcargs:
            try:
                api_runner = item.funcargs.get("api_runner")
                detail_str = json.dumps(api_runner.detail, indent=4, ensure_ascii=False)
                allure.attach(
                    detail_str,
                    name="API请求日志",
                    attachment_type=allure.attachment_type.JSON
                )
            except Exception as e:
                print(f"API日志获取失败: {e}")