from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from abc import ABC, abstractmethod
from selenium import webdriver
import selenium.common
import utils.config
import jdatetime
import requests
import json
import time


class Authentication(ABC):

    def __init__(self):
        self.chrome_executable_path = utils.config.CHROME_EXECUTABLE_PATH
        self.driver = None

    @abstractmethod
    def account_login(self):
        pass

    # @abstractmethod
    # def send_order(self, order_type, ticker_isin_code, quantity, price):
    #     pass

    # @abstractmethod
    # def cancel_order(self):
    #     pass

    # @abstractmethod
    # def get_liquidity(self):
    #     pass

    # @abstractmethod
    # def market_watch(self):
    #     pass


class MofidBroker(Authentication, ABC):

    def __init__(self, username, password):

        Authentication.__init__(self)

        self.username = username
        self.password = password
        self.LOGIN_TOKEN = None

        self.base_login_url = "https://d.easytrader.emofid.com"
        self.mobile_login_url = "https://mobile.emofid.com"
        self.alternative_login_url = "https://mofidonline.com/login?checkmobile=false"

        self.order_url = "https://easy-api.emofid.com/easy/api/OmsOrder"
        self.get_liquidity_url = "https://easy-api.emofid.com/easy/api/Money/GetRemain"
        self.get_user_data_url = "https://easy-api.emofid.com/easy/api/account/GetUserBourseCode"
        # self.get_transactions_url = "https://easy-api.emofid.com/easy/api/transaction/getd"
        self.get_assets_url = "https://easy-api.emofid.com/easy/api/portfolio"
        self.market_watch_url = "https://easy-api.emofid.com/easy/api/MarketWatch"
        self.get_orders_history_url = "https://easy-api.emofid.com/easy/api/OrderHistory/getd"
        self.get_symbol_data_url = "https://easy-api.emofid.com/easy/api/MarketData/GetSymbolDetailsData/{}/SymbolInfo"
        self.get_symbol_market_depth_url = "https://easy-api.emofid.com/easy/api/MarketData/GetSymbolDetailsData/{}/marketDepth"
        # self.alternative_get_instrument_data_url = "https://easy-api.emofid.com/easy/api/MarketData/GetSymbolDetailsData/{}/StockOrderData"
        # self.get_current_orders_url = "https://easy-api.emofid.com/easy/api/Order"
        self.cancel_order_url = "https://easy-api.emofid.com/easy/api/OmsOrder/{}"

    def account_login(self):

        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL", "browser": "ALL"}

        chrome_options = webdriver.ChromeOptions()
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})

        try:
            self.driver = webdriver.Chrome(executable_path=self.chrome_executable_path, options=chrome_options,
                                           desired_capabilities=capabilities)

        except selenium.common.SessionNotCreatedException:

            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options,
                                           desired_capabilities=capabilities)

        self.driver.get(self.mobile_login_url)

        timeout = 60

        try:
            element_present = expected_conditions.presence_of_element_located((By.ID, 'Username'))
            WebDriverWait(self.driver, timeout).until(element_present)

        except selenium.common.TimeoutException:
            print("Timed out waiting for page to load")

        username_form = self.driver.find_element(By.ID, 'Username')
        password_form = self.driver.find_element(By.ID, 'Password')

        username_form.send_keys(self.username)
        password_form.send_keys(self.password)

        login_button = self.driver.find_element(By.ID, 'submit_btn')

        login_button.click()

        try:
            element_present = expected_conditions.presence_of_element_located((By.ID, 'root'))
            WebDriverWait(self.driver, timeout).until(element_present)

        except selenium.common.TimeoutException:
            print("Timed out waiting for page to load")

        time.sleep(2)

        logs = self.driver.get_log("performance")

        log_was_successful = False

        # while log_was_successful is False:

        for index, log in enumerate(logs):
            log = json.loads(log["message"])["message"]
            if log['method'] == 'Network.requestWillBeSent':
                if 'request' in log['params']:
                    if 'headers' in log['params']['request']:
                        if 'Authorization' in log['params']['request']['headers']:
                            self.LOGIN_TOKEN = log['params']['request']['headers']['Authorization']
                            # log_was_successful = True
                            break
        else:
            time.sleep(1)

        return self.LOGIN_TOKEN

    def get_portfolio(self):

        while self.LOGIN_TOKEN is None:

            try:
                self.account_login()
                # time.sleep(2)

            except selenium.common.NoSuchElementException:
                pass

        headers_template = {'Accept': 'application/json, text/plain, */*',
                            'Authorization': self.LOGIN_TOKEN,
                            'Referer': 'https://mobile.emofid.com/',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                          '(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': '"Windows"'}

        request_response = requests.get(url=self.get_assets_url, headers=headers_template)

        # self.LOGIN_TOKEN = None  # reset token value
        # self.driver.quit()

        return request_response

    def get_liquidity(self):

        while self.LOGIN_TOKEN is None:

            try:
                self.account_login()
                time.sleep(2)

            except selenium.common.NoSuchElementException:
                pass

        headers_template = {'Accept': 'application/json, text/plain, */*',
                            'Authorization': self.LOGIN_TOKEN,
                            'DNT': '1',
                            'Referer': 'https://mobile.emofid.com/',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                          '(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': '"Windows"'}

        request_response = requests.get(url=self.get_liquidity_url, headers=headers_template)

        # self.LOGIN_TOKEN = None  # reset token value
        # self.driver.quit()

        return request_response

    def send_order(self, order_type, ticker_isin_code, quantity, price):

        while self.LOGIN_TOKEN is None:

            try:
                self.account_login()
                # time.sleep(2)

            except selenium.common.NoSuchElementException:
                pass

        headers_template = {'Accept': 'application/json, text/plain, */*',
                            'Authorization': self.LOGIN_TOKEN,
                            'Content-Type': 'application/json',
                            'DNT': '1',
                            'Referer': 'https://mobile.emofid.com/',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                          '(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': '"Windows"'}

        payload_template = {"isin": ticker_isin_code,
                            "financeId": 1,
                            "quantity": quantity,
                            "price": price,
                            "side": order_type,
                            "validityType": 74,
                            "validityDateJalali": str(jdatetime.datetime.today().date()).replace('-', '/'),
                            "easySource": 1,
                            "referenceKey": None,
                            "cautionAgreementSelected": False}

        request_response = requests.post(url=self.order_url, headers=headers_template, json=payload_template)

        # self.LOGIN_TOKEN = None  # reset token value
        # self.driver.quit()

        return request_response

    def get_orders_list_details(self):
        while self.LOGIN_TOKEN is None:

            try:
                self.account_login()
                # time.sleep(2)

            except selenium.common.NoSuchElementException:
                pass

        headers_template = {'Accept': 'application/json, text/plain, */*',
                            'Authorization': self.LOGIN_TOKEN,
                            'Content-Type': 'application/json',
                            'DNT': '1',
                            'Referer': 'https://mobile.emofid.com/',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                          '(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': '"Windows"'}

        request_response = requests.get(url=self.order_url, headers=headers_template)

        # self.LOGIN_TOKEN = None  # reset token value
        # self.driver.quit()

        return request_response

    def cancel_order(self, order_id):
        while self.LOGIN_TOKEN is None:

            try:
                self.account_login()
                # time.sleep(2)

            except selenium.common.NoSuchElementException:
                pass

        headers_template = {'Accept': 'application/json, text/plain, */*',
                            'Authorization': self.LOGIN_TOKEN,
                            'Content-Type': 'application/json',
                            'DNT': '1',
                            'Referer': 'https://mobile.emofid.com/',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                          '(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': '"Windows"'}

        request_response = requests.delete(url=self.cancel_order_url.format(order_id), headers=headers_template)

        # self.LOGIN_TOKEN = None  # reset token value
        # self.driver.quit()

        return request_response

    def market_watch(self, watchlist_name):

        while self.LOGIN_TOKEN is None:

            try:
                self.account_login()
                # time.sleep(2)

            except selenium.common.NoSuchElementException:
                pass

        headers_template = {'Accept': 'application/json, text/plain, */*',
                            'Authorization': self.LOGIN_TOKEN,
                            'Content-Type': 'application/json',
                            'DNT': '1',
                            'Referer': 'https://mobile.emofid.com/',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                          '(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': '"Windows"'}

        request_response = json.loads(requests.get(url=self.market_watch_url, headers=headers_template).text)

        watching_tickers = None

        for watchlist in request_response['watchCategoryItems']:
            try:
                if watchlist['name'] == watchlist_name:
                    watching_tickers = watchlist
                    break
            except KeyError:
                pass

        # self.LOGIN_TOKEN = None  # reset token value
        # self.driver.quit()

        return watching_tickers

    def get_orders_history(self, count=50):

        while self.LOGIN_TOKEN is None:

            try:
                self.account_login()
                # time.sleep(2)

            except selenium.common.NoSuchElementException:
                pass

        headers_template = {'Accept': 'application/json, text/plain, */*',
                            'Authorization': self.LOGIN_TOKEN,
                            'Referer': 'https://mobile.emofid.com/',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                          '(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                            'DNT': 1,
                            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': '"Windows"'}

        payload_template = {'page': 0,
                            'size': count}

        request_response = requests.post(url=self.get_orders_history_url, headers=headers_template,
                                         json=payload_template)

        # self.LOGIN_TOKEN = None  # reset token value
        # self.driver.quit()

        return request_response

    def get_symbol_data(self, ticker_isin_code):
        while self.LOGIN_TOKEN is None:

            try:
                self.account_login()
                # time.sleep(2)

            except selenium.common.NoSuchElementException:
                pass

        headers_template = {'Accept': 'application/json, text/plain, */*',
                            'Authorization': self.LOGIN_TOKEN,
                            'Referer': 'https://mobile.emofid.com/',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                          '(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': '"Windows"'}

        request_response = requests.get(url=self.get_symbol_data_url.format(ticker_isin_code), headers=headers_template)

        # self.LOGIN_TOKEN = None  # reset token value
        # self.driver.quit()

        return request_response

    def get_symbol_market_depth(self, ticker_isin_code):
        while self.LOGIN_TOKEN is None:

            try:
                self.account_login()
                # time.sleep(2)

            except selenium.common.NoSuchElementException:
                pass

        headers_template = {':authority': 'easy-api.emofid.com',
                            ':method': 'GET',
                            ':path': '/easy/api/MarketData/GetSymbolDetailsData/{}/marketDepth'.format(ticker_isin_code),
                            ':schem': 'https',
                            'Accept': 'application/json, text/plain, */*',
                            'Authorization': self.LOGIN_TOKEN,
                            'dnt': 1,
                            'origin': 'https://mobile.emofid.com/',
                            'Referer': 'https://mobile.emofid.com/',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                          '(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': '"Windows"',
                            'sec-fetch-dest': 'empty',
                            'sec-fetch-mode': 'cors',
                            'sec-fetch-site': 'same-site'}

        request_response = requests.get(url=self.get_symbol_market_depth_url.format(ticker_isin_code), headers=headers_template)

        # self.LOGIN_TOKEN = None  # reset token value
        # self.driver.quit()

        return request_response


class ExirBroker(Authentication, ABC):

    def __init__(self, broker_name, username, password):
        Authentication.__init__(self)

        self.broker_name = broker_name  # TODO: Automate
        self.username = username
        self.password = password
        self.COOKIE = None

        self.base_login_url = "https://{}.exirbroker.com/exir/login?returnUrl=%2F"
        self.mobile_login_url = "https://{}.exirbroker.com/mobile/#view/login.html"
        self.get_portfolio_url = "https://{}.exirbroker.com/api/v1/restapi/customers/livePortfolio?size=-1"
        self.get_orders_history_url = "https://{broker}.exirbroker.com/api/v1/restapi/customers/orderBook?lang=fa&size=10&page=1&orderBy=entryDateTime_desc&startDate={start}&endDate={end}"
        self.market_watch_url = "https://{}.exirbroker.com/api/v1/user/watchLists"
        pass

    def account_login(self):

        desired_cap = {'browser': 'chrome', 'browser_version': 'latest', 'os': 'Windows', 'os_version': '10',
                       'build': 'Python Sample Build', 'name': 'Pop-ups testing', "chromeOptions": {}}

        desired_cap["chromeOptions"]["excludeSwitches"] = ["disable-popup-blocking"]

        desired_cap["chromeOptions"]["javascript.enabled"] = [False]

        chrome_options = webdriver.ChromeOptions()
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})

        try:
            self.driver = webdriver.Chrome(executable_path=self.chrome_executable_path, options=chrome_options,
                                           desired_capabilities=desired_cap)

        except selenium.common.SessionNotCreatedException:

            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options,
                                           desired_capabilities=desired_cap)

        self.driver.get(self.mobile_login_url.format(self.broker_name))

        timeout = 60

        try:
            element_present = expected_conditions.presence_of_element_located((By.CSS_SELECTOR,
                                                                               '.fa.fa-times-circle.close'))
            WebDriverWait(self.driver, timeout).until(element_present)

        except selenium.common.TimeoutException:
            print("Timed out waiting for page to load")

        close_pop_up_button = self.driver.find_element(By.CSS_SELECTOR, '.fa.fa-times-circle.close')

        close_pop_up_button.click()

        try:
            element_present = expected_conditions.presence_of_element_located((By.ID, 'username'))
            WebDriverWait(self.driver, timeout).until(element_present)

        except selenium.common.TimeoutException:
            print("Timed out waiting for page to load")

        username_form = self.driver.find_element(By.ID, 'username')
        password_form = self.driver.find_element(By.ID, 'password')

        username_form.send_keys(self.username)
        password_form.send_keys(self.password)

        login_button = self.driver.find_element(By.CSS_SELECTOR, '.btn.btn-block')

        login_button.click()

        try:
            element_present = expected_conditions.presence_of_element_located((By.ID, 'changePasswordView'))
            WebDriverWait(self.driver, timeout).until(element_present)

        except selenium.common.TimeoutException:
            print("Timed out waiting for page to load")

        time.sleep(2)

        logs = self.driver.get_log("performance")

        log_was_successful = False

        while log_was_successful is False:

            for index, log in enumerate(logs[::-1]):
                log = json.loads(log["message"])["message"]
                if log['method'] == 'Network.requestWillBeSentExtraInfo':
                    if 'headers' in log['params']:
                        if 'Cookie' in log['params']['headers']:
                            self.COOKIE = log['params']['headers']['Cookie']
                            log_was_successful = True
                            break
            else:
                time.sleep(1)

        return self.COOKIE

    def get_portfolio(self):

        while self.COOKIE is None:

            try:
                self.account_login()

            except selenium.common.NoSuchElementException:
                pass

        header_template = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                           'Accept-Encoding': 'gzip, deflate, br',
                           'Accept-Language': 'en-US,en;q=0.9,fa;q=0.8',
                           'Connection': 'keep-alive',
                           'Content-Type': 'application/json; charset=utf-8',
                           'Cookie': self.COOKIE,
                           'DNT': '1',
                           'Host': '{}.exirbroker.com'.format(self.broker_name),
                           'Referer': 'https://{}.exirbroker.com/mobile/'.format(self.broker_name),
                           'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                           'sec-ch-ua-mobile': '?0',
                           'sec-ch-ua-platform': 'Windows',
                           'Sec-Fetch-Dest': 'empty',
                           'Sec-Fetch-Mode': 'cors',
                           'Sec-Fetch-Site': 'same-origin',
                           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                           'X-App-N': None,
                           'X-Requested-With': 'XMLHttpRequest'}

        request_response = json.loads(requests.get(url=self.get_portfolio_url.format(self.broker_name), headers=header_template).text)

        portfolio = list(filter(lambda asset: asset['remainQty'] > 0, request_response['result']))

        self.COOKIE = None  # reset token value
        self.driver.quit()

        return portfolio

    def get_orders_history(self, starting_date, ending_date):
        while self.COOKIE is None:

            try:
                self.account_login()

            except selenium.common.NoSuchElementException:
                pass

        header_template = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                           'Accept-Encoding': 'gzip, deflate, br',
                           'Accept-Language': 'en-US,en;q=0.9,fa;q=0.8',
                           'Connection': 'keep-alive',
                           'Content-Type': 'application/json; charset=utf-8',
                           'Cookie': self.COOKIE,
                           'DNT': '1',
                           'Host': '{}.exirbroker.com'.format(self.broker_name),
                           'Referer': 'https://{}.exirbroker.com/mobile/'.format(self.broker_name),
                           'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                           'sec-ch-ua-mobile': '?0',
                           'sec-ch-ua-platform': 'Windows',
                           'Sec-Fetch-Dest': 'empty',
                           'Sec-Fetch-Mode': 'cors',
                           'Sec-Fetch-Site': 'same-origin',
                           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                           'X-App-N': None,
                           'X-Requested-With': 'XMLHttpRequest'}

        url = self.get_orders_history_url.format(broker=self.broker_name, start=starting_date, end=ending_date)
        request_response = requests.get(url=url, headers=header_template)

        self.COOKIE = None  # reset token value
        self.driver.quit()

        return request_response

    def market_watch(self, watchlist_name=None):
        while self.COOKIE is None:

            try:
                self.account_login()

            except selenium.common.NoSuchElementException:
                pass

        header_template = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                           'Accept-Encoding': 'gzip, deflate, br',
                           'Accept-Language': 'en-US,en;q=0.9,fa;q=0.8',
                           'Connection': 'keep-alive',
                           'Content-Type': 'application/json; charset=utf-8',
                           'Cookie': self.COOKIE,
                           'DNT': '1',
                           'Host': '{}.exirbroker.com'.format(self.broker_name),
                           'Referer': 'https://{}.exirbroker.com/mobile/'.format(self.broker_name),
                           'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                           'sec-ch-ua-mobile': '?0',
                           'sec-ch-ua-platform': 'Windows',
                           'Sec-Fetch-Dest': 'empty',
                           'Sec-Fetch-Mode': 'cors',
                           'Sec-Fetch-Site': 'same-origin',
                           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                           'X-App-N': None}

        request_response = json.loads(requests.post(url=self.market_watch_url.format(self.broker_name),
                                                    headers=header_template, json={}).text)

        watching_tickers = None

        for watchlist in request_response['watchLists']:
            try:
                if watchlist['watchListName'] == watchlist_name:
                    watching_tickers = watchlist
                    break
            except KeyError:
                pass

        self.COOKIE = None  # reset token value
        self.driver.quit()

        return watching_tickers
