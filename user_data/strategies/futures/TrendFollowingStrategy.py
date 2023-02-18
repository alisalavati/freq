from freqtrade.strategy.interface import IStrategy
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter
from typing import Dict, List
import talib.abstract as ta

class TrendFollowingStrategy(IStrategy):
    timeframe = '5m'

    # Buy hyperspace params:
    buy_params = {
        "buy_trailing": 0.98,
        "buy_rsi": 53,
        "buy_ema_1": 38,
        "buy_ema_2": 68,
        "buy_williamsr": -98
    }

    # Sell hyperspace params:
    sell_params = {
        "sell_trailing": 1.01,
        "sell_rsi": 43,
        "sell_ema_1": 60,
        "sell_ema_2": 28,
        "sell_williamsr": -34
    }

    # ROI table:
    minimal_roi = {
        "0": 0.05,
        "30": 0.02,
        "60": 0.01,
        "120": 0
    }

    # Stoploss:
    stoploss = -0.1

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    # Optimal timeframe for the strategy
    optimal_timeframe = '5m'

    # Optional order type mapping
    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force mapping
    order_time_in_force = {
        'buy': 'gtc',
        'sell': 'gtc'
    }

    def populate_indicators(self, dataframe: dict, metadata: dict) -> dict:
        # EMA
        dataframe['ema_1'] = ta.EMA(dataframe, timeperiod=14)
        dataframe['ema_2'] = ta.EMA(dataframe, timeperiod=28)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Williams %R
        dataframe['williams_r'] = ta.WILLR(dataframe, timeperiod=14)

        return dataframe

    def populate_buy_trend(self, dataframe: dict, metadata: dict) -> dict:
        dataframe.loc[
            (
                (dataframe['close'] > dataframe['ema_1']) &
                (dataframe['ema_1'] > dataframe['ema_2']) &
                (dataframe['rsi'] > self.buy_rsi.value) &
                (dataframe['williams_r'] < self.buy_williamsr.value)
            ),
            'buy'
        ] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: dict, metadata: dict) -> dict:
        dataframe.loc[
            (
                (dataframe['close'] < dataframe['ema_1']) &
                (dataframe['ema_1'] < dataframe['ema_2']) &
                (dataframe['rsi'] < self.sell_rsi.value) &
                (dataframe['williams_r'] > self.sell_williamsr.value)
            ),
            'sell'
        ] = 1
