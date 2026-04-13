from utils.helpers import get_cases
import allure
import pytest

@allure.feature("Web UI 测试")
@pytest.mark.parametrize("test_case", get_cases("web"),ids=lambda x: f"{x['name']}")
def test_web_cases(test_case, web_runner):
    web_runner.run(test_case)