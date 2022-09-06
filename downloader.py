import config
import requests
from typing import Dict
from warnings import filterwarnings
from requests.adapters import HTTPAdapter, Retry
from concurrent.futures import ThreadPoolExecutor

filterwarnings("ignore")

header = {"Connection": "keep-alive",
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}

stock_data_url = config.TSE_MARKET_WATCH_PLUS


def get_stocks_information() -> Dict:

    stocks_info = dict()

    session = requests.Session()

    retries = Retry(total=10, backoff_factor=0.01)

    session.mount('http://', HTTPAdapter(max_retries=retries))

    data = session.get(stock_data_url, headers=header)

    for content in data.text.split(";")[1:]:

        content = content.split(",")
        ticker_id = content[0]
        try:
            if content[1].isdigit() is False:
                keys = ['id', 'ir_index', 'ticker', 'company', 'last_update', 'first_price', 'closing_price',
                        'current_price',  'transactions_count', 'transactions_volume', 'transactions_value',
                        'day_lowest_price', 'day_highest_price', 'yesterday_price', 'EPS', 'base_volume', 'unknown_1',
                        'unknown_2', 'unknown_3', 'highest_possible_price', 'lowest_possible_price', 'total_shares_count',
                        'unknown_4']
                if len(content) == 23:
                    stocks_info[ticker_id] = dict(zip(keys[1:], content[1:]))
                else:
                    stocks_info[ticker_id] = dict(zip(keys[1:], content[:23][1:]))
            else:
                order_description = {'seller_count': content[2], 'buyer_count': content[3],
                                     'buyer_price': content[4], 'seller_price': content[5],
                                     'buyer_volume': content[6], 'seller_volume': content[7]}
                try:

                    if "orderbook" not in stocks_info[ticker_id].keys():
                        stocks_info[ticker_id]["orderbook"] = {content[1]: order_description}
                    else:
                        stocks_info[ticker_id]["orderbook"][content[1]] = order_description

                except Exception:
                    pass

        except Exception:
            pass

    return stocks_info


def get_all_data_concurrent() -> Dict:
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.submit(get_stocks_information).result()
    return results
