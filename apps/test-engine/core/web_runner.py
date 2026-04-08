import time
import allure
from playwright.sync_api import sync_playwright, expect
from utils import read_file, get_locator_str, replace_variables, get_user

class WebRunner:
    def __init__(self):
        # 启动 Playwright
        self._playwright = sync_playwright().start()
        # 无头模式launch 浏览器
        self.browser = self._playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()

    def close(self):
        # 关闭 Playwright 资源
        if hasattr(self, 'page'):
            self.page.close()
        if hasattr(self, '_browser'):
            self.browser.close()
        if hasattr(self, '_playwright'):
            self._playwright.stop()

    def run(self,cases: list = None):
        if not cases:
            return

        for case in cases:
            file = read_file(case)
            enable, name, steps, assertions, test_data, reuse_browser = (
                file.get(k) for k in ['enable', 'name', 'steps', 'assertions', 'test_data', 'reuse_browser']
            )

            if not enable:
                print(f"跳过用例-未启用：{name}")
                continue

            if not test_data:
                print(f"跳过用例-缺少测试数据：{name}")
                continue

            # 如果不复用，就新建一个浏览器实例来执行用例
            if not reuse_browser:
                self.page.close()
                self.browser.close()
                self.browser = self._playwright.chromium.launch(headless=False)
                self.page = self.browser.new_page()

            # 用不同数据执行用例
            for data in test_data:
                self.run_case(name, steps, assertions, data)

        self.close()

    def run_case(self, name, steps, assertions, data):
        """执行单组 DDT 测试数据"""
        user_id = data.get('user_id')
        user_info = get_user(user_id)

        # Allure 动态标记
        allure.dynamic.title(f"{name} - {user_id}")
        allure.dynamic.story(name)

        # 遍历步骤，标记 Allure 步骤
        for i,step in enumerate(steps):
            with allure.step(f"步骤{i+1}: {step['name']}"):
                self.handle_step(step,user_info)

        # 遍历断言，标记 Allure 断言步骤
        for i,assertion in enumerate(assertions):
            with allure.step(f"断言{i+1}: {assertion['name']}"):
                self.handle_assertion(assertion, user_info)

    def handle_step(self,step,data):
        """执行单个步骤的逻辑"""
        action = step['action']
        value = replace_variables(step['value'], data) if 'value' in step else None  # 替换变量
        locator = get_locator_str(step)
        if action == 'open':
            self.page.goto(value)
        elif action == 'sleep':
            time.sleep(step['time'])  # 替换成异步非阻塞 sleep
        elif action == 'wait_for_url':
            self.page.wait_for_function(f"window.location.href.includes('{value}')")
            self.page.wait_for_load_state("load")  # 等待页面资源加载完毕
        elif action == 'input':
            self.page.fill(locator, value)
        elif action == 'click':
            self.page.click(locator,force=True)
        elif action == 'update_attributes':
            element = self.page.locator(locator)
            # 使用 JavaScript 设置元素属性
            for attr_name, attr_value in step['attributes'].items():
                element.evaluate(f"(el) => {{ el.setAttribute('{attr_name}', '{attr_value}') }}")

    def handle_assertion(self, assertion, data):
        """处理断言"""
        assertion_type = assertion['type']
        expected = replace_variables(assertion['expected'], data)

        if assertion_type == 'text':
            locator = get_locator_str(assertion)
            element = self.page.locator(locator)
            actual_text = element.text_content()
            assert expected in actual_text, f"期望文本 '{expected}' 不在元素文本 '{actual_text}' 中"
        elif assertion_type == 'page_url':
            actual_url = self.page.url
            assert expected == actual_url, f"期望URL '{expected}' 不等于实际URL '{actual_url}'"
        else:
            raise ValueError(f"不支持的断言类型：{assertion_type}")