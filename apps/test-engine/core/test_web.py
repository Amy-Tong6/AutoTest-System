from utils import get_cases
from web_runner import WebRunner
import allure

@allure.feature("Web 自动化测试")
def test_web_cases():
    cases = get_cases("web")
    WebRunner().run(cases)





