import json
import time
from abc import ABC, abstractmethod

import jdatetime
import requests
import selenium.common
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import execution_engine.config as config


class Authentication(ABC):
    def __init__(self):
        self.chrome_executable_path = config.CHROME_EXECUTABLE_PATH
        self.driver = None

    @abstractmethod
    def account_login(self):
        pass


class MofidBroker(Authentication, ABC):
    def __init__(self, username, password):
        Authentication.__init__(self)
        self.username = username
        self.password = password
        self.login_token = None

    def _headers(self):
        return {
            "Accept": "application/json, text/plain, */*",
            "Authorization": self.login_token,
            "Referer": "https://mobile.emofid.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            "sec-ch-ua-mobile": "?0",
        }

    def account_login(self):
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL", "browser": "ALL"}
        chrome_options = webdriver.ChromeOptions()
        chrome_options.set_capability(
            "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}
        )
        try:
            self.driver = webdriver.Chrome(
                executable_path=self.chrome_executable_path,
                options=chrome_options,
                desired_capabilities=capabilities,
            )
        except selenium.common.SessionNotCreatedException:

            self.driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=chrome_options,
                desired_capabilities=capabilities,
            )
        self.driver.get(self.mobile_login_url)
        timeout = 60
        try:
            element_present = expected_conditions.presence_of_element_located(
                (By.ID, "Username")
            )
            WebDriverWait(self.driver, timeout).until(element_present)
        except selenium.common.TimeoutException:
            print("Timed out waiting for page to load")
        username_form = self.driver.find_element(By.ID, "Username")
        password_form = self.driver.find_element(By.ID, "Password")
        username_form.send_keys(self.username)
        password_form.send_keys(self.password)
        login_button = self.driver.find_element(By.ID, "submit_btn")
        login_button.click()
        try:
            element_present = expected_conditions.presence_of_element_located(
                (By.ID, "root")
            )
            WebDriverWait(self.driver, timeout).until(element_present)
        except selenium.common.TimeoutException:
            print("Timed out waiting for page to load")
        time.sleep(2)
        logs = self.driver.get_log("performance")
        log_was_successful = False
        while log_was_successful is False:
            for index, log in enumerate(logs):
                log = json.loads(log["message"])["message"]
                if log["method"] == "Network.requestWillBeSent":
                    if "request" in log["params"]:
                        if "headers" in log["params"]["request"]:
                            if "Authorization" in log["params"]["request"]["headers"]:
                                self.LOGIN_TOKEN = log["params"]["request"]["headers"][
                                    "Authorization"
                                ]
                                log_was_successful = True
                                break
            else:
                time.sleep(1)
        return self.login_token

    def get_portfolio(self):
        while self.login_token is None:
            try:
                self.account_login()
                # time.sleep(2)
            except selenium.common.NoSuchElementException:
                pass
        request_response = requests.get(
            url=self.get_assets_url, headers=self._headers()
        )
        return request_response

    def get_liquidity(self):
        while self.login_token is None:
            try:
                self.account_login()
                time.sleep(2)
            except selenium.common.NoSuchElementException:
                pass
        request_response = requests.get(
            url=self.get_liquidity_url, headers=self._headers()
        )
        return request_response

    def send_order(self, order_type, ticker_isin_code, quantity, price):

        while self.LOGIN_TOKEN is None:

            try:
                self.account_login()
                # time.sleep(2)

            except selenium.common.NoSuchElementException:
                pass

        payload_template = {
            "isin": ticker_isin_code,
            "financeId": 1,
            "quantity": quantity,
            "price": price,
            "side": order_type,
            "validityType": 74,
            "validityDateJalali": str(jdatetime.datetime.today().date()).replace(
                "-", "/"
            ),
            "easySource": 1,
            "referenceKey": None,
            "cautionAgreementSelected": False,
        }

        request_response = requests.post(
            url=self.order_url, headers=self._headers(), json=payload_template
        )

        return request_response

    def market_watch(self, watchlist_name):

        while self.LOGIN_TOKEN is None:

            try:
                self.account_login()
                # time.sleep(2)

            except selenium.common.NoSuchElementException:
                pass

        request_response = json.loads(
            requests.get(url=self.market_watch_url, headers=self._headers()).text
        )

        watching_tickers = None

        for watchlist in request_response["watchCategoryItems"]:
            try:
                if watchlist["name"] == watchlist_name:
                    watching_tickers = watchlist
                    break
            except KeyError:
                pass

        return watching_tickers

    def get_orders_history(self, count=50):
        while self.LOGIN_TOKEN is None:
            try:
                self.account_login()
            except selenium.common.NoSuchElementException:
                pass
        payload_template = {"page": 0, "size": count}
        request_response = requests.post(
            url=self.get_orders_history_url,
            headers=self._headers(),
            json=payload_template,
        )
        return request_response

    def get_symbol_data(self, ticker_isin_code):
        while self.LOGIN_TOKEN is None:
            try:
                self.account_login()
                # time.sleep(2)
            except selenium.common.NoSuchElementException:
                pass
        request_response = requests.get(
            url=self.get_symbol_data_url.format(ticker_isin_code),
            headers=self._headers(),
        )

        return request_response

    def get_symbol_market_depth(self, ticker_isin_code):
        while self.LOGIN_TOKEN is None:
            try:
                self.account_login()
            except selenium.common.NoSuchElementException:
                pass

        headers_template = {
            ":authority": "easy-api.emofid.com",
            ":method": "GET",
            ":path": "/easy/api/MarketData/GetSymbolDetailsData/{}/marketDepth".format(
                ticker_isin_code
            ),
            ":schem": "https",
            "Accept": "application/json, text/plain, */*",
            "Authorization": self.login_token,
            "dnt": 1,
            "origin": "https://mobile.emofid.com/",
            "Referer": "https://mobile.emofid.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }

        request_response = requests.get(
            url=self.get_symbol_market_depth_url.format(ticker_isin_code),
            headers=headers_template,
        )

        return request_response
