from api.streamtools import *
from api.commands import *
from utils.setup_loger import setup_logger


class DefaultCloseSignal:
    def __init__(self):
        self.DCS_logger = setup_logger("DCS_logger", "beta\log\DCS_logger.log")

    def init(
        self,
        api: object,
        position_data: dict,
        sl_start: float = 0.35,
        tp_min: float = 0.5,
        tp_max: float = 0.1,
        asymetyric_tp:float = 0.5
    ):
        if position_data["transactions_data"] == None:
            print('transactions_data = None')
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

        self.walet_stream = WalletStream(api=self.api)
        self.price_data = PositionObservator(
            api=api, symbol=self.symbol, order_no=self.order
        )
        self.status_to_close = False

        if self.cmd == 1:
            self.multiplier_value = 1
        else:
            self.multiplier_value = -1

        self.acc_earnings_stage = False


    def subscribe_data(self):
        self.walet_stream.subscribe()
        self.price_data.subscribe()

    def read_data(self):
        self.walet_stream.streamread()
        self.price_data.streamread()

    def get_current_percentage(self):
        try:
            return (self.price_data.profit / self.margin) * 100
        except:
            pass

    def obeserve_and_react(self):

        if self.price_data.minute_1.any() and self.get_current_percentage() > 0 and self.get_current_percentage() < self.sl_start:
            print('earnings')
            if self.get_current_percentage() > self.sl_start * self.asymetyric_tp:
                self.acc_earnings_stage = True
                self.sl_start = self.sl_start * self.asymetyric_tp
            if self.acc_earnings_stage == True:
                if self.get_current_percentage() < self.sl_start * self.asymetyric_tp:
                    close_data = close_position(
                        api=self.api,
                        symbol=self.symbol, 
                        position=self.position,
                        volume=self.volume, 
                        cmd=self.cmd)
                    self.status_to_close = True
                else:
                    pass
            else:
                pass
        elif self.price_data.minute_1.any() and self.get_current_percentage() < 0:
            print('candle without earnings')
            try:
                if self.get_current_percentage() > (-1 * self.sl_start):
                    pass
                else:
                    close_data = close_position(
                        api=self.api,
                        symbol=self.symbol, 
                        position=self.position,
                        volume=self.volume, 
                        cmd=self.cmd)
                    self.status_to_close = True
            except:
                self.DCS_logger.warning(
                    f'ORDER {self.order} POSITION {self.position} - \
                    CANT MONITOR FIRST STAGE [TAKEPROFIT-DCS]')
        elif not self.price_data.minute_1.any():
            print('lack of candle')
            try:
                if self.get_current_percentage() > (-1 * self.sl_start):
                    pass
                else:
                    close_data = close_position(
                        api=self.api,
                        symbol=self.symbol, 
                        position=self.position,
                        volume=self.volume, 
                        cmd=self.cmd)
                    self.status_to_close = True
            except:
                self.DCS_logger.warning(
                    f'ORDER {self.order} POSITION {self.position} - \
                    CANT MONITOR FIRST STAGE [TAKEPROFIT-DCS]')
        else:
            print('error',(not self.price_data.minute_1.any()), type(self.price_data.minute_1))
            close_data = close_position(
                        api=self.api,
                        symbol=self.symbol, 
                        position=self.position,
                        volume=self.volume, 
                        cmd=self.cmd)
            self.status_to_close = True

    def run(self):
        self.subscribe_data()
        while self.status_to_close == False:
            self.read_data()
            try:
                self.obeserve_and_react()
            except:
                pass









    # def first_stage_monitor(self):
    #     if (self.price_data.profit / self.margin) < self.sl_start :
    #         self.close_signal = True
    #         return self.close_signal
    #     else:
    #         self.close_signal = False
    #         pass

    # def get_1M_candle_dir(self):
    #     return self.price_data.minute_1[0, 2] - self.price_data.minute_1[0, 1]

    # def take_profit(self, candle):
    #     time_to_candle_end = (
    #         60000 - (self.price_data.curent_price[0, 6] - (candle[0, 0]) - 60000)
    #     ) / 1000

    #     max_tp_price = candle[0, 1] + (candle[0, 2] - candle[0, 1]) * self.tp_max
    #     min_tp_price = candle[0, 1] + (candle[0, 2] - candle[0, 1]) * self.tp_min

    #     if self.price_data.minute_1[0, 2] - self.price_data.minute_1[0, 1] > 0 and self.cmd :

    #         return self.close_signal
