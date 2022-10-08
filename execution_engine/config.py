from dataclasses import dataclass

TSE_MARKET_WATCH_PLUS = (
    "http://www.tsetmc.com/tsev2/data/MarketWatchPlus.aspx?h=0&r=10392282875"
)
TSE_ISNT_INFO_URL = "http://www.tsetmc.com/tsev2/data/instinfofast.aspx?i={}&c=0&e=1"

CHROME_EXECUTABLE_PATH = (
    "/Users/sina/tmp/trade_exec/exectrade/execution_engine/drivers/chromedriver"
)
MOFID = {
    "base_login_url": "https://d.easytrader.emofid.com",
    "mobile_login_url": "https://mobile.emofid.com",
    "alternative_login_url": "https://mofidonline.com/login?checkmobile=false",
    "order_url": "https://easy-api.emofid.com/easy/api/OmsOrder",
    "get_liquidity_url": "https://easy-api.emofid.com/easy/api/Money/GetRemain",
    "get_user_data_url": (
        "https://easy-api.emofid.com/easy/api/account/GetUserBourseCode"
    ),
    # self.get_transactions_url = "https://easy-api.emofid.com/easy/api/transaction/getd"
    "get_assets_url": "https://easy-api.emofid.com/easy/api/portfolio",
    "market_watch_url": "https://easy-api.emofid.com/easy/api/MarketWatch",
    "get_orders_history_url": (
        "https://easy-api.emofid.com/easy/api/OrderHistory/getd"
    ),
    "get_symbol_data_url": "https://easy-api.emofid.com/easy/api/MarketData/GetSymbolDetailsData/{}/SymbolInfo",
    "get_symbol_market_depth_url": "https://easy-api.emofid.com/easy/api/MarketData/GetSymbolDetailsData/{}/marketDepth",
}


@dataclass
class Influx:
    token = "7VqIFiNN5RmJX9_CmaNiCo5jKTGkC0dchJIv0MSiJi7jwTN3Ziw89T0i2JmtX9uvBl91Ehy4i0f0oUk9k8GZPQ=="
    org = "delta"
    bucket = "stocks"
