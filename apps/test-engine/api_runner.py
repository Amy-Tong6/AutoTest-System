import allure
import pytest
import requests
from utils.helpers import replace_variables, get_config

class ApiRunner:
    def __init__(self, client_id):
        # 初始化-作为前置处理
        api_access_token = get_config(client_id, "api_access_token")
        self.session = requests.session()
        self.session.headers = {
            "Authorization": f"Bearer {api_access_token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10"
        }
        self.detail = None

    def close(self):
        self.session = None

    def run(self, test_case):
        enable, name, steps, data = test_case.get("enable"), test_case.get("name"), test_case.get("steps"), test_case.get("data")

        # Allure 动态标记
        allure.dynamic.title(f"{name}")
        allure.dynamic.story(name)

        # 检查用例是否启用
        if not enable:
            pytest.skip(f"用例未启用")

        for i, step in enumerate(steps):
            with allure.step(f"步骤{i + 1}: {step['name']}"):
                self._handle_step(step, data)

    def _handle_step(self, step, data):
        """执行单步接口"""
        # 1. 变量准备
        base_url = data.get("base_url")
        path = step.get("path")
        full_url = base_url + replace_variables(path, data)
        method, json_data = step.get("method"), step.get("json")
        print(f"【请求】{method} {full_url} {json_data}")

        # 2. 发送请求
        response = self._send_request(method, full_url, json_data)
        resp_json = response.json() if response.text else {}

        # 3. 保存请求响应详情
        try:
            response_body = response.json()
        except:
            response_body = response.text
        self.detail = {
            "url": full_url,
            "method": method,
            "request_headers": {**self.session.headers, "Authorization": "Bearer ***",},
            "request_body": json_data,
            "status_code": response.status_code,
            "response_headers": dict(response.headers),
            "response_body": response_body
        }

        # 4. 提取结果
        if "extract" in step:
            for k,expr in step["extract"].items(): # 遍历字典键值对
                value = self._extract_value(resp_json, expr) # 从结果中，提取出表达式对应的值
                data[k] = value # 存到用例数据中

        # 5. 断言
        if "assert" in step:
            self._assert_result(response, step["assert"]) # 对本step的结果断言

    def _send_request(self, method, url, json_data):
        if method == "GET":
            return self.session.get(url)
        elif method == "POST":
            return self.session.post(url, json=json_data)
        elif method == "PUT":
            return self.session.put(url, json=json_data)
        elif method == "PATCH":
            return self.session.patch(url, json=json_data)
        elif method == "DELETE":
            return self.session.delete(url)
        raise Exception(f"不支持的请求方法：{method}")

    @staticmethod
    def _extract_value(resp_json, expr: str):
        if not expr.startswith("json."):
            return expr
        paths = expr.replace("json.", "").split(".")
        result = resp_json
        for p in paths:
            if isinstance(result, dict):
                result = result.get(p)
            else:
                return None
        return result

    def _assert_result(self, response, assertions):
        for expr, value in assertions.items():
            if expr.startswith("json"):
                actual = self._extract_value(response.json(), expr)
            elif expr == "status_code":
                actual = response.status_code
            else:
                raise Exception(f"不支持的断言表达式：{expr}")
            assert value == actual, f"期望{expr}={value}，实际{expr}={actual}"
