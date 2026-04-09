from utils import get_cases
import allure
import pytest

@allure.feature("Web UI 测试")
@pytest.mark.parametrize("test_case", get_cases("web"),ids=lambda x: f"{x['name']}-{x['data'].get('user_id')}")
def test_web_cases(test_case, web_runner):
    test_case['enable'] or pytest.skip(f"用例未启用")
    web_runner.run(test_case)