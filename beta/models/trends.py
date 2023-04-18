from api.client import Client
from api.streamtools import AssetObservator


class MovingAVG():

    def __init__(self,api:Client,symbol:str,period:int=1) -> None:
        self.api = api
        self.symbol = symbol
        self.period = period
        self.base_data = None
        
        self.observator = AssetObservator(api=api,symbol=self.symbol,period=period)

    def data_stream(self):
        self.observator.subscribe()
        while self.api.connection_stream == True:
            self.observator.streamread()
            self.base_data = self.observator.base_data

    


    


        
        
