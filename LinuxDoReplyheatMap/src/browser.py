import os
import string
import logging
from DrissionPage import ChromiumOptions, ChromiumPage

def create_proxy_auth_extension(proxy_host, proxy_port, proxy_username, proxy_password, scheme="http", plugin_path=None):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "16YUN Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """
    background_js = string.Template(
        """
        var config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                },
                bypassList: ["localhost"]
            }
        };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
        );
        """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    os.makedirs(plugin_path, exist_ok=True)
    with open(os.path.join(plugin_path, "manifest.json"), "w+") as f:
        f.write(manifest_json)
    with open(os.path.join(plugin_path, "background.js"), "w+") as f:
        f.write(background_js)
    return os.path.join(plugin_path)

class BrowserManager:
    def __init__(self, browser_path, proxy_conf, turnstile_patch_path):
        self.browser_path = browser_path
        self.proxy_conf = proxy_conf
        self.turnstile_patch_path = turnstile_patch_path
        self.page = None
        self.logger = logging.getLogger(__name__)

    def setup_browser(self):
        co = ChromiumOptions()
        co.set_argument("--no-proxy-server")
        if self.browser_path:
            co.set_browser_path(self.browser_path)
        if self.proxy_conf is not None:
            proxy_auth_plugin_path = create_proxy_auth_extension(
                plugin_path=self.proxy_conf["plugin_path"],
                proxy_host=self.proxy_conf["host"],
                proxy_port=self.proxy_conf["port"],
                proxy_username=self.proxy_conf["user"],
                proxy_password=self.proxy_conf["password"],
            )
            co.add_extension(path=proxy_auth_plugin_path)
        co.add_extension(path=self.turnstile_patch_path)
        self.page = ChromiumPage(co)
        return self.page

    def handle_turnstile_challenge(self):
        try:
            challenge_solution = self.page.ele("@name=cf-turnstile-response", timeout=3)
            if not challenge_solution:
                self.logger.error("未找到cf-turnstile-response元素")
                return False
            challenge_wrapper = challenge_solution.parent()
            if not challenge_wrapper:
                self.logger.error("未找到父容器")
                return False
            if not hasattr(challenge_wrapper, 'shadow_root') or not challenge_wrapper.shadow_root:
                self.logger.error("未找到shadow root")
                return False
            challenge_iframe = challenge_wrapper.shadow_root.ele("tag:iframe", timeout=2)
            if not challenge_iframe:
                self.logger.error("未找到iframe")
                return False
            iframe_body = challenge_iframe.ele("tag:body", timeout=2)
            if not iframe_body:
                self.logger.error("未找到iframe body")
                return False
            if not hasattr(iframe_body, 'shadow_root') or not iframe_body.shadow_root:
                self.logger.error("未找到iframe body的shadow root")
                return False
            challenge_button = iframe_body.shadow_root.ele("tag:input", timeout=2)
            if challenge_button:
                challenge_button.click()
                self.logger.info("验证码按钮点击成功")
                return True
            else:
                self.logger.error("未找到验证码按钮")
                return False
        except Exception as e:
            self.logger.error(f"处理验证码时出错: {e}")
            return False

    def cf_bypass(self, get_page_status_js_func):
        max_attempts = 5
        for i in range(max_attempts):
            status = get_page_status_js_func()
            if status == 200:
                return
            elif status != 403:
                self.logger.info(f"检测到状态码为{status}，无需点击验证码，直接返回")
                return
            self.logger.info(f"第{i+1}次点击验证，当前状态码: {status}")
            attempt = 0
            while attempt < max_attempts:
                # 每次重试前都检查状态码
                status = get_page_status_js_func()
                if status == 200:
                    self.logger.info(f"重试前检测到状态码为200，提前返回")
                    return
                elif status != 403:
                    self.logger.info(f"重试前检测到状态码为{status}，无需继续点击，直接返回")
                    return
                try:
                    if self.handle_turnstile_challenge():
                        status = get_page_status_js_func()
                        if status == 200:
                            return
                        elif status != 403:
                            self.logger.info(f"点击后检测到状态码为{status}，无需继续点击，直接返回")
                            return
                        else:
                            break  # 点击成功但403未解除，跳出内层重试
                    else:
                        self.logger.info(f"第{i+1}轮第{attempt+1}次点击失败，重试...")
                except Exception as e:
                    self.logger.error(f"点击验证码时异常: {e}")
                attempt += 1
                import time
                time.sleep(0.3)
            import time
            time.sleep(0.5) 