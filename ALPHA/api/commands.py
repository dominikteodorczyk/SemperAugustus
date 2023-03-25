import logging
import json
from ast import literal_eval


class RetrievingTradingData():

    def __init__(self) -> None:
        pass


    def command_rtd(func): #wraper do wysyłki komend rtd 
        def wrapped(**kwargs):
            return func(**kwargs)

    def getAllSymbols(self):
        packet = {
	        "command": "getAllSymbols"
        }
        return packet

    def getCalendar(self):
        packet = {
	    "command": "getCalendar"
        }
        return packet

    def getChartLastRequest(self, parameters:dict):
        '''
        {
            "command": "getChartLastRequest",
            "arguments": {
                "info": CHART_LAST_INFO_RECORD
            }
        }
        http://developers.xstore.pro/documentation/#getChartLastRequest
        '''
        packet = {
            "command": "getChartLastRequest",
            "arguments": parameters
        }
        return packet

    def getChartRangeRequest(self, parameters:dict):
        '''
        {
            "command": "getChartRangeRequest",
            "arguments": {
                "info": CHART_RANGE_INFO_RECORD
            }
        }
        http://developers.xstore.pro/documentation/#getChartRangeRequest
        '''
        packet = {
            "command": "getTickPrices",
            "arguments": parameters
        }
        return packet
    
    def getCommissionDef(self, parameters:dict):
        '''
        {
            "command": "getCommissionDef",
            "arguments": {
                "symbol": "T.US",
                "volume": 1.0
            }
        }
        http://developers.xstore.pro/documentation/#getCommissionDef
        '''
        packet = {
            "command": "getTickPrices",
            "arguments": parameters
        }
        return packet

    def getCurrentUserData(self):
        '''
        http://developers.xstore.pro/documentation/#getCurrentUserData
        '''
        packet = {
            "command": "getCurrentUserData"
        }
        return packet

    def getIbsHistory (self, parameters:dict):
        '''
        {
            "command": "getIbsHistory",
            "arguments": {
                "end": 1395053810991,
                "start": 1394449010991
            }
        }
        http://developers.xstore.pro/documentation/#getIbsHistory
        '''
        packet = {
            "command": "getTickPrices",
            "arguments": parameters
        }
        return packet
    
    def getMarginLevel(self):
        '''
        {
            "command": "getMarginLevel"
        }
        http://developers.xstore.pro/documentation/#getMarginLevel
        '''
        packet = {
            "command": "getMarginLevel"
        }
        return packet
    
    def getMarginTrade(self, parameters:dict):
        '''
        {
            "command": "getMarginTrade",
            "arguments": {
                "symbol": "EURPLN",
                "volume": 1.0
            }
        }
        http://developers.xstore.pro/documentation/#getMarginTrade
        '''
        packet = {
            "command": "getMarginTrade",
            "arguments": parameters
        }
        return packet

    def getNews(self, parameters:dict):
        '''
        {
            "command": "getNews",
            "arguments": {
                "end": 0,
                "start": 1275993488000
            }
        }
        http://developers.xstore.pro/documentation/#getNews
        '''
        packet = {
            "command": "getNews",
            "arguments": parameters
        }
        return packet

    def getProfitCalculation(self, parameters:dict):
        '''
        {
            "command": "getProfitCalculation",
            "arguments": {
                "closePrice": 1.3000,
                "cmd": 0,
                "openPrice": 1.2233,
                "symbol": "EURPLN",
                "volume": 1.0
            }
        }
        http://developers.xstore.pro/documentation/#getProfitCalculation
        '''
        packet = {
            "command": "getProfitCalculation",
            "arguments": parameters
        }
        return packet

    def getServerTime(self, parameters:dict):
        '''
        {
            "command": "getServerTime"
        }
        http://developers.xstore.pro/documentation/#getServerTime
        '''
        packet = {
            "command": "getServerTime"
        }
        return packet

    def getStepRules(self, parameters:dict):
        '''
        {
            "command": "getStepRules"
        }
        http://developers.xstore.pro/documentation/#getStepRules
        '''
        packet = {
            "command": "getStepRules"
        }
        return packet
    
    def getSymbol(self, parameters:dict):
        '''
        {
            "command": "getSymbol",
            "arguments": {
                "symbol": "EURPLN"
            }
        }
        http://developers.xstore.pro/documentation/#getSymbol
        '''
        packet = {
            "command": "getSymbol",
            "arguments": parameters
        }
        return packet
    
    def getTickPrices(self, parameters:dict):
        '''
        {
            "command": "getTickPrices",
            "arguments": {
                "level": 0,
                "symbols": ["EURPLN", "AGO.PL", ...],
                "timestamp": 1262944112000
            }
        }
        http://developers.xstore.pro/documentation/#getTickPrices
        '''
        packet = {
            "command": "getTickPrices",
            "arguments": parameters
        }
        return packet
    
    def getTradeRecords(self, parameters:dict):
        '''
        {
            "command": "getTradeRecords",
            "arguments": {
                "orders": [7489839, 7489841, ...]
            }
        }
        http://developers.xstore.pro/documentation/#getTradeRecords
        '''
        packet = {
            "command": "getTradeRecords",
            "arguments": parameters
        }
        return packet

    def getTrades(self, parameters:dict):
        '''
        {
            "command": "getTrades",
            "arguments": {
                "openedOnly": true
            }
        }
        http://developers.xstore.pro/documentation/#getTrades
        '''
        packet = {
            "command": "getTrades",
            "arguments": parameters
        }
        return packet
    

    def getTradesHistory(self, parameters:dict):
        '''
        {
            "command": "getTradesHistory",
            "arguments": {
                "end": 0,
                "start": 1275993488000
            }
        }
        http://developers.xstore.pro/documentation/#getTradesHistory
        '''
        packet = {
            "command": "getTradesHistory",
            "arguments": parameters
        }
        return packet
    
    def getTradingHours(self, parameters:dict):
        '''
        {
            "command": "getTradingHours",
            "arguments": {
                "symbols": ["EURPLN", "AGO.PL", ...]
            }
        }
        http://developers.xstore.pro/documentation/#getTradingHours
        '''
        packet = {
            "command": "getTradingHours",
            "arguments": parameters
        }
        return packet

    def getVersion(self):
        '''
        {
            "command": "getVersion"
        }
        http://developers.xstore.pro/documentation/#getVersion
        '''
        packet = {
            "command": "getVersion"
        }
        return packet
    
    def ping(self):
        '''
        {
            "command": "ping"
        }
        http://developers.xstore.pro/documentation/#ping
        '''
        packet = {
            "command": "ping"
        }
        return packet

    def tradeTransaction(self, parameters:dict):
        '''
        {
            "command": "tradeTransaction",
            "arguments": {
                "tradeTransInfo": TRADE_TRANS_INFO
            }
        }
        http://developers.xstore.pro/documentation/#tradeTransaction
        '''
        packet = {
            "command": "tradeTransaction",
            "arguments": parameters
        }
        return packet
    
    def tradeTransactionStatus(self, parameters:dict):

        packet = {
            "command": "tradeTransactionStatus",
            "arguments": parameters
        }
        return packet


def get_trade_info(response:dict, order_no:int):
    transactions_data = None
    for i in response['returnData']:
        if i['order2'] == order_no:
            transactions_data = {
                'symbol': i['symbol'],
                'order': order_no,
                'position': i['position'],
                'cmd': i['cmd'],
                'volume': i['volume'],
                'open_price': i['open_price'],
                'open_time': i['open_time']
            }
            break
    return transactions_data


def get_trades(api, order_no=None):
    response = api.send_n_return( {
        "command": "getTrades",
        "arguments": {
            "openedOnly": True
        }
    })
    transactions_data = get_trade_info(response, order_no)
    return transactions_data


def buy_transaction(api:object, symbol:str, volume:float):
    buy_arguments = {
                    "tradeTransInfo": {
                        "cmd": 0,
                        "customComment": "",
                        "expiration": 0,
                        "order": 0,
                        "price": 1.4,
                        "sl": 0,
                        "tp": 0,
                        "symbol": symbol,
                        "type": 0,
                        "volume": volume
                        }
                    }
          
    buy_response = api.send_n_return({
        "command": "tradeTransaction", 
        "arguments": buy_arguments
         })

    if buy_response['status'] is True:
        order_no = buy_response["returnData"]["order"]
        position = {
            'order_no': order_no, 
            'transactions_data': get_trades(api = api, order_no = order_no)
            }
        logging.info(f'[{symbol} BUY] transaction opened (order no: {order_no})')
        return position
    else:
        logging.info(f'[{symbol} BUY] Transaction failed')


def sell_transaction(api:object, symbol:str, volume:float):
    sell_arguments = {
                    "tradeTransInfo": {
                        "cmd": 1,
                        "customComment": "",
                        "expiration": 0,
                        "order": 0,
                        "price": 1.4,
                        "sl": 0,
                        "tp": 0,
                        "symbol": symbol,
                        "type": 0,
                        "volume": volume
                        }
                    }
          
    sell_response = api.send_n_return({
        "command": "tradeTransaction", 
        "arguments": sell_arguments
         })

    if sell_response['status'] is True:
        order_no = sell_response["returnData"]["order"]
        position = {
            'order_no': order_no, 
            'transactions_data': get_trades(api = api, order_no = order_no)
            }
        logging.info(f'[{symbol} SELL] transaction opened (order no: {order_no})')
        return position
    else:
        logging.info(f'[{symbol} SELL] Transaction failed')  


