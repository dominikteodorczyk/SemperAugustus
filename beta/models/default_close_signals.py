from api.streamtools import *

class DefaultCloseSignal():

    def __init__(self,api,open_price, stop_loss_lvl:float, position_margin:float):
        self.open_price = open_price
        self.sl_lvl = stop_loss_lvl
        self.margin = position_margin
        self.close_signal = False

        self.current_price = None
        self.current_wallet_banace = None
        self.current_return = None
        self.minute_1 = None
        self.minutes_5 = None
        self.minutes_15 = None
        
        self.walet_stream = WalletStream(api=api)
        self.price_data = PositionObservator(api=api,symbol=self.symbol)
        self.status_to_close = False

    def subscribe_data(self):
        self.walet_stream.subscribe()
        self.price_data.subscribe()

    def read_data(self):
        self.current_wallet_banace = self.walet_stream.balance
        self.current_price = self.price_data.curent_price
        self.current_return = self.price_data.profit
        self.minute_1 = self.price_data.minute_1
        self.minutes_5 = self.price_data.minute_5
        self.minutes_15 = self.price_data.minute_15

    def sefault_close_position(self):
        pass

    def run_position(self):
        self.subscribe_data()
        while self.status_to_close is False:
            self.walet_stream.streamread()
            self.price_data.streamread()
            self.read_data()

    def first_stage_monitor(self, actual_profit):
        if (actual_profit/self.margin) < self.sl_lvl:
            self.close_signal = True
            return self.close_signal
        else:
            self.close_signal = False
            pass

    def main_stage(self):
        self.close_signal = True
        return self.close_signal
    

