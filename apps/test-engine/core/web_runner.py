import time
import allure
from playwright.sync_api import sync_playwright, expect
from helpers import get_locator_str, replace_variables, get_user

headless = True

class WebRunner:
    def __init__(self):
        # 启动 Playwright
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=headless)
        self._page = self._browser.new_page()

    def close(self):
        # 关闭 Playwright 资源
        self._page.close()
        self._browser.close()
        self._playwright.stop()

    def reopen(self):
        """重新打开浏览器"""
        self._page.close()
        self._browser.close()
        self._browser = self._playwright.chromium.launch(headless=headless)
        self._page = self._browser.new_page()

    def run(self, test_case: dict):
        """执行单组 DDT 测试数据"""
        name, steps, assertions, data, reuse_browser = (
            test_case.get(k) for k in ['name', 'steps', 'assertions', 'data', 'reuse_browser']
        )
        user_id = data.get('user_id')
        user_info = get_user(user_id)

        # Allure 动态标记
        allure.dynamic.title(f"{name} - {user_id}")
        allure.dynamic.story(name)

        # 重启浏览器（如果需要）
        if not reuse_browser:
            self.reopen()

        # 遍历步骤，标记 Allure 步骤
        for i,step in enumerate(steps):
            with allure.step(f"步骤{i+1}: {step['name']}"):
                self._handle_step(step, user_info)

    def _handle_step(self,step,data):
        """执行单个步骤的逻辑"""
        action = step['action']
        value = replace_variables(step['value'], data) if 'value' in step else None  # 替换变量
        locator = get_locator_str(step)
        if action == 'open':
            self._page.goto(value)
        elif action == 'sleep':
            time.sleep(step['time'])  # 替换成异步非阻塞 sleep
        elif action == 'wait_for_url':
            self._page.wait_for_function(f"window.location.href.includes('{value}')")
            self._page.wait_for_load_state("load")  # 等待页面资源加载完毕
        elif action == 'input':
            self._page.fill(locator, value)
        elif action == 'click':
            self._page.click(locator)
        elif action == 'update_attributes':
            element = self._page.locator(locator)
            # 使用 JavaScript 设置元素属性
            for attr_name, attr_value in step['attributes'].items():
                element.evaluate(f"(el) => {{ el.setAttribute('{attr_name}', '{attr_value}') }}")
        elif action == 'assert':
            self._handle_assertion(step, data)

    def _handle_assertion(self, step, data):
        """处理断言"""
        type = step['type']
        expected = replace_variables(step['expected'], data)

        if type == 'text':
            locator = get_locator_str(step)
            element = self._page.locator(locator)
            actual_text = element.text_content()
            assert expected in actual_text, f"期望文本 '{expected}' 不在元素文本 '{actual_text}' 中"
        else:
            raise ValueError(f"不支持的断言类型：{type}")

    def screenshot(self):
        return self._page.screenshot()