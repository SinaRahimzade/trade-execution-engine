from typing import Dict, List


def buy_signals(tickers_information: Dict, threshold=0.97) -> List:
    for ticker, information in tickers_information.items():
        if int(information['current_price']) / int(information['yesterday_price']) < threshold:
            yield ticker


def sell_signals(tickers_information: Dict, threshold=1.02) -> List:
    for ticker, information in tickers_information.items():
        if int(information['current_price']) / int(information['yesterday_price']) > threshold:
            yield ticker
