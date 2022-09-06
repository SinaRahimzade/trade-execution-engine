from downloader import get_all_data_concurrent
from signals import buy_signals, sell_signals
import pytse_client as ptc


whole_market_data = get_all_data_concurrent()
tickers_list = ['ساینا', 'فولاد', 'بنو', 'شتولی', 'وخارزم', 'مفاخر', 'خودرو']
tickers_id_list = [ptc.Ticker(ticker).url.split('=')[-1] for ticker in tickers_list]

tickers_data = dict(zip(tickers_list, [whole_market_data[ticker] for ticker in tickers_id_list]))

tickers_to_buy = list(buy_signals(tickers_data))
ticker_to_sell = list(sell_signals(tickers_data))
