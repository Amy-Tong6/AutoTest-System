import time
from playwright.sync_api import sync_playwright, expect
from utils import read_file, get_locator_str, replace_variables, get_user

class WebRunner:
    def __init__(self):
        self.total = 0
        self.skipped = 0
        self.executed = 0
        self.success = 0
        self.failed = 0
        # 启动 Playwright
        self._playwright = sync_playwright().start()
        # 无头模式
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
        self.total = len(cases)
        for case in cases:
            self.run_case(case)
        self.close()

    def run_case(self,case):
        """执行单个用例的逻辑，支持 DDT 模式"""
        file = read_file(case)
        enable = file.get('enable', False)
        name = file.get('name', 'Unknown')
        steps = file.get('steps', [])
        assertions = file.get('assertions', [])
        test_data = file.get('test_data', [])
        reuse_browser = file.get('reuse_browser', False)
        
        if not enable:
            print(f"跳过用例-未启用：{name}")
            self.skipped += 1
            return

        if not test_data:
            print(f"跳过用例-缺少测试数据：{name}")
            self.skipped += 1
            return

        # DDT 模式：为每个测试数据执行一次
        print(f"执行 DDT 用例：{name}，共 {len(test_data)} 组数据")
        # 如果不复用，就新建一个浏览器实例来执行用例
        if not reuse_browser:
            self.page.close()
            self.browser.close()
            self.browser = self._playwright.chromium.launch(headless=False)
            self.page = self.browser.new_page()

        for data in test_data:
            self.run_ddt(name, steps, assertions, data)
    
    def run_ddt(self, name, steps, assertions, data):
        """执行单组 DDT 测试数据"""
        user_id = data.get('user_id')
        user_info = get_user(user_id)
        print(f">>> 开始执行 [{name}-{user_id}] 的测试 <<<")
        case_failed = False
        if not self.handle_steps(steps,user_info):
            case_failed = True

        if not self.handle_assertions(assertions, user_info):
            case_failed = True

        if case_failed:
            self.failed += 1
            print(f">>> 账户 [{name}-{user_id}] 测试失败 <<<")
        else:
            self.success += 1
            print(f">>> 账户 [{name}-{user_id}] 测试通过 <<<")

    def handle_steps(self, steps,data)-> bool:
        """执行步骤列表，如果任何步骤失败返回 False，否则 True"""
        for step in steps:
            try:
                self.handle_step(step,data)
            except Exception as e:
                self.logger.error(f"步骤执行失败：{e}")
                return False
        return True

    def handle_step(self,step,data):
        """执行单个步骤的逻辑，成功则返回 True，失败则返回 False"""
        print(f"执行 step:{step['name']}")
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

    def handle_assertions(self, assertions,data):
        """处理断言列表，如果任何断言失败返回 False，否则 True"""
        if not assertions:
            return True
        for assertion in assertions:
            try:
                if not self.handle_assertion(assertion,data):
                    return False
            except Exception as e:
                self.logger.error(f"断言执行失败：{e}")
                return False
        return True

    def handle_assertion(self, assertion,data)-> bool:
        """处理断言"""
        print(f"执行assertion：{assertion['name']}")
        assertion_type = assertion['type']
        expected = replace_variables(assertion['expected'], data)

        if assertion_type == 'text':
            locator = get_locator_str(assertion)
            element = self.page.locator(locator)
            expect(element).to_contain_text(expected)
        elif assertion_type == 'page_url':
            expect(self.page).to_have_url(expected)
        else:
            self.logger.error(f"不支持的断言类型：{assertion_type}")
            return False

        return True