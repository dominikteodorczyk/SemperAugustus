from src.api.streamtools import *
from src.api.commands import *
from src.utils.setup_loger import setup_logger
from threading import Thread


class DefaultCloseSignal:
    def __init__(self):
        self.DCS_logger = setup_logger("DCS_logger", "DCS_logger.log")
        self.closedata = None

    def set_params(
        self,
        api: object,
        position_data: dict,
        sl_start: float = 2,
        tp_min: float = 0.5,
        tp_max: float = 0.1,
        asymetyric_tp: float = 0.5,
    ):
        if position_data["transactions_data"] == None:
            print("transactions_data = None")

        self.api = api
        self.symbol = position_data["transactions_data"]["symbol"]
        self.order = position_data["order_no"]
        self.position = position_data["transactions_data"]["position"]
        self.open_price = position_data["transactions_data"]["cmd"]
        self.margin = position_data["margin"]
        self.cmd = position_data["transactions_data"]["cmd"]
        self.volume = position_data["transactions_data"]["volume"]
        self.asymetyric_tp = asymetyric_tp

        self.sl_start = sl_start
        self.tp_min = tp_min
        self.tp_max = tp_max

        self.price_data = PositionObservator(
            api=api, symbol=self.symbol, order_no=self.order
        )
        self.status_to_close = False

        if self.cmd == 1:
            self.multiplier_value = 1
            self.as_bid_position = 0
            self.cs_function = self.sell_take_profit_signal
        else:
            self.multiplier_value = -1
            self.as_bid_position = 1
            self.cs_function = self.buy_take_profit_signal

        self.not_earnings_stage = True
        self.yes_earnings_stage = False

        self.acc_earnings_stage_0 = False
        self.acc_earnings_stage_05 = False
        self.acc_earnings_stage_1 = False
        self.acc_earnings_stage_5 = False
        self.acc_earnings_stage_15 = False

    def subscribe_data(self):
        self.price_data.subscribe()

    def read_data(self):
        while self.status_to_close == False:
            self.price_data.stream()

    def get_current_percentage(self):
        try:
            return (self.price_data.profit / self.margin) * 100
        except:
            pass

    def get_candle_mean(self, cendle_data):
        mean_prince = (cendle_data[0, 2] - cendle_data[0, 1]) / 2
        return cendle_data[0, 1] + mean_prince

    def control_asset_easy(self):
        if self.cmd == 0:
            while self.status_to_close == False:
                self.buy_take_profit_signal()
                sleep(0.001)   
        if self.cmd == 1:
            while self.status_to_close == False:
                self.sell_take_profit_signal()
                sleep(0.001)             



    def calculate_easy_buy_cs(self, candle, current_price):
        mean_candle_value = self.get_candle_mean(candle)
        
        
        if current_price > mean_candle_value:
            pass
        else:
            self.closedata = close_position(
                api=self.api,symbol=self.symbol,position=self.position,
                volume=self.volume,cmd=self.cmd,)

            self.status_to_close = True

    def calculate_easy_sell_cs(self, candle, current_price):
        mean_candle_value = self.get_candle_mean(candle)
        
        if current_price < mean_candle_value:
            pass
        else:
            self.closedata = close_position(
                api=self.api,symbol=self.symbol,position=self.position,
                volume=self.volume,cmd=self.cmd,)

            self.status_to_close = True


    def buy_take_profit_signal(self):

        try:
            current_price = self.price_data.curent_price[0, self.as_bid_position]
            current_percentage = self.get_current_percentage()
            if current_percentage <= 0:

                if current_percentage > (-1 * self.sl_start):
                    pass
                else:
                    self.closedata = close_position(
                                    api=self.api,
                                    symbol=self.symbol,
                                    position=self.position,
                                    volume=self.volume,
                                    cmd=self.cmd,
                                )
                    self.status_to_close = True

            if current_percentage > 0:
                if self.price_data.minute_15.any():
                    self.calculate_easy_buy_cs(self.price_data.minute_15,current_price)
                elif self.price_data.minute_5.any():
                    self.calculate_easy_buy_cs(self.price_data.minute_5,current_price)
                elif self.price_data.minute_1.any():
                    pass
                    #self.calculate_easy_buy_cs(self.price_data.minute_1,current_price)
                elif not self.price_data.minute_1.any():
                    pass
                else:
                    self.DCS_logger.info('PASS')

        except:
            pass
        

    def sell_take_profit_signal(self):
        try:
            current_price = self.price_data.curent_price[0, self.as_bid_position]
            current_percentage = self.get_current_percentage()
            
            if current_percentage <= 0:

                if current_percentage > (-1 * self.sl_start):
                    sleep(0.1)
                    pass
                else:
                    self.closedata = close_position(
                                    api=self.api,
                                    symbol=self.symbol,
                                    position=self.position,
                                    volume=self.volume,
                                    cmd=self.cmd,
                                )
                    self.status_to_close = True

            if current_percentage > 0:
                if self.price_data.minute_15.any():
                    self.calculate_easy_sell_cs(self.price_data.minute_15,current_price)
                elif self.price_data.minute_5.any():
                    self.calculate_easy_sell_cs(self.price_data.minute_5,current_price)
                elif self.price_data.minute_1.any():
                    pass
                    #self.calculate_easy_sell_cs(self.price_data.minute_1,current_price)
                elif not self.price_data.minute_1.any():
                    pass
                else:
                    self.DCS_logger.info('PASS')


        except:
            pass
        
    def run(self):
        self.subscribe_data()
        read_thread = Thread(target=self.read_data, args=())
        control_thread = Thread(target=self.control_asset_easy, args=())

        read_thread.start()
        control_thread.start()

        read_thread.join()
        control_thread.join()



