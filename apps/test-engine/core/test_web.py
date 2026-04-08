from utils import get_cases
from web_runner import WebRunner
import allure

@allure.feature("Web UI 测试")
@allure.story("GitHub 登录测试")
def test_web_cases():
    with allure.step("读取 Web 用例文件"):
        cases = get_cases("web")
    
    with allure.step("执行 Web 用例"):
        runner = WebRunner()
        runner.run(cases)
    
    with allure.step("验证结果"):
        # 断言：至少有一个用例成功
        assert runner.success > 0, f"没有成功的用例：成功 {runner.success}，失败 {runner.failed}"
        allure.attach(f"成功用例数: {runner.success}\n失败用例数: {runner.failed}", name="测试统计", attachment_type=allure.attachment_type.TEXT)





