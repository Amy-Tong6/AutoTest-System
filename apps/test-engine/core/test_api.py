from helpers import get_cases
import allure
import pytest

@allure.feature("API 测试")
@pytest.mark.parametrize("test_case", get_cases("api"),ids=lambda x: f"{x['name']}")
def test_api_cases(test_case, api_runner): # 发现api_runner会先执行conftest里的api_runner
    test_case['enable'] or pytest.skip(f"用例未启用")
    api_runner.run(test_case)