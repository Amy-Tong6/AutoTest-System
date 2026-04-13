import allure
import pytest
from web_runner import WebRunner
from api_runner import ApiRunner
import json

# ==============================================
# 🔥 注册 --client 参数
# ==============================================
def pytest_addoption(parser):
    # 注册命令行参数 --client
    parser.addoption(
        "--client",
        action="store",
        default="test",
        help="要运行的客户：github / ali / test"
    )

# ==============================================
# 🔥 只给 WEB 用例使用
# ==============================================
@pytest.fixture(scope="module")
def web_runner(request):
    # 前置：
    # 从命令行获取 --client 参数
    client = request.config.getoption("--client")
    print(f"\n🚀 开始运行 Web Runner，当前客户：{client}")
    runner = WebRunner()

    yield runner  # 提供给测试用例

    # 后置：
    print("\n🏁 关闭浏览器")
    runner.close()

# ==============================================
# 🔥 只给 API 用例使用
# ==============================================
@pytest.fixture(scope="module")
def api_runner(request):
    # 前置：
    # 从命令行获取 --client 参数
    client = request.config.getoption("--client")

    print(f"\n🚀 启动 API Runner，当前客户：{client}")
    runner = ApiRunner(client)

    yield runner  # 提供给测试用例

    # 后置：
    print("\n🏁 关闭")
    runner.close()


# ==============================================
# 🔥 内置钩子可以监听用例结果, 失败展示截图 or 日志
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