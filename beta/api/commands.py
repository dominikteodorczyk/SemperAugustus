import logging
from time import sleep
import pandas
import numpy as np


def get_trades(api, order_no=None):
    """
    Retrieves trading data for a specific order number from the specified API.

    Args:
        api: An object representing the API to use for retrieving the data.
        order_no: An optional integer representing the order number.

    Returns:
        A dictionary containing the trading data for the specified order, 
        or None if no data was found.
    """
    message = {"command": "getTrades", "arguments": {"openedOnly": True}}

    data_recive = False
    while data_recive == False:
        sleep(1)
        try:
            response = api.send_n_return(message)
            for trade in response["returnData"]:
                if trade["order2"] == order_no:
                    data_recive = True
                    return {
                        "symbol": trade["symbol"],
                        "order": order_no,
                        "position": trade["position"],
                        "cmd": trade["cmd"],
                        "volume": trade["volume"],
                        "open_price": trade["open_price"],
                        "open_time": trade["open_time"],
                    }

            return None
        except:
            pass

def get_margin(api:object, symbol:str, volume:float):

    message = {
        "command": "getMarginTrade", 
        "arguments": {
            "symbol": symbol,
            "volume": volume
        }}

    response = api.send_n_return(message)
    return response["returnData"]["margin"]


def buy_transaction(api: object, symbol: str, volume: float) -> dict:
    """Opens a buy transaction and returns the position information.

    Args:
        api: An object representing the API used to execute the transaction.
        symbol: A string representing the symbol of the asset to be bought.
        volume: A float representing the volume of the asset to be bought.

    Returns:
        A dictionary containing the order number and transaction data for the 
        position opened, or None if the transaction failed.

    """
    # Define arguments for the buy transaction.
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
            "volume": volume,
        }
    }

    # Send the buy transaction request.
    buy_response = api.send_n_return(
        {"command": "tradeTransaction", "arguments": buy_arguments}
    )
    margin = get_margin(api=api, symbol=symbol, volume=volume)

    try:
        order_no = buy_response["returnData"]["order"]
        transactions_data = get_trades(api=api, order_no=order_no)
        position = {
            "order_no": order_no,
            "margin" : margin,
            "transactions_data": transactions_data
        }
    except:
        logging.info(f"[{symbol} BUY] Transaction failed")

    if buy_response["status"] == True and transactions_data != None and margin != None:
        position = {
            "order_no": order_no,
            "margin" : margin,
            "transactions_data": transactions_data
        }
        logging.info(
            f"[{symbol} BUY] transaction opened (order no: {order_no})"
        )
        return position
    else:
        logging.info(f"[{symbol} BUY] transaction failed")


def sell_transaction(api: object, symbol: str, volume: float) -> dict:
    """Opens a sell transaction and returns the position information.

    Args:
        api: An object representing the API used to execute the transaction.
        symbol: A string representing the symbol of the asset to be bought.
        volume: A float representing the volume of the asset to be bought.

    Returns:
        A dictionary containing the order number and transaction data for 
        the position opened, or None if the transaction failed.

    """
    # Define arguments for the buy transaction.
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
            "volume": volume,
        }
    }

    # Send the buy transaction request.
    sell_response = api.send_n_return(
        {"command": "tradeTransaction", "arguments": sell_arguments}
    )
    margin = get_margin(api=api, symbol=symbol, volume=volume)

    try:
        order_no = sell_response["returnData"]["order"]
        transactions_data = get_trades(api=api, order_no=order_no)
        position = {
            "order_no": order_no,
            "margin" : margin,
            "transactions_data": transactions_data
        }
    except:
        logging.info(f"[{symbol} SELL] Transaction failed")

    if sell_response["status"] and transactions_data:
        position = {
            "order_no": order_no,
            "margin" : margin,
            "transactions_data": transactions_data
        }
        logging.info(
            f"[{symbol} SELL] transaction opened (order no: {order_no})"
        )
        return position
    else:
        logging.info(f"[{symbol} SELL] transaction failed")



def close_position(
        api: object, symbol: str, position:int, volume: float, cmd:int):
    
    close_arguments = {
        "tradeTransInfo": {
            "cmd": cmd,
            "customComment": "",
            "expiration": 0,
            "order": position,
            "price": 1.4,
            "sl": 0,
            "tp": 0,
            "symbol": symbol,
            "type": 2,
            "volume": volume,
        }
    }

    # Send the buy transaction request.
    close_status = False
    while close_status == False:
        close_response = api.send_n_return(
            {"command": "tradeTransaction", "arguments": close_arguments}
        )
        if close_response["status"] == True:
            close_status = True
            server_time = api.send_n_return(
                {"command": "getServerTime"}
                )["returnData"]["time"]
            data_recive = False

            while data_recive == False:
                sleep(1)
                try:    
                    trades_stats = api.send_n_return(
                        {"command":"getTradesHistory",
                        "arguments":{
                            "end": 0,
                            "start": server_time - 10000
                        }})
                    for trade in trades_stats["returnData"]:
                        if trade["position"] == position:
                            data_recive = True
                            return {
                                "symbol": trade["symbol"],
                                "order": trade["order2"],
                                "position": trade["position"],
                                "cmd": trade["cmd"],
                                "volume": trade["volume"],
                                "profit": trade["profit"],
                                "open_price": trade["open_price"],
                                "open_time": trade["open_time"],
                                "close_price":trade["close_price"],
                                "close_time": trade["close_time"],} 
                except:
                    pass

def get_historical_candles(api, symbol:str, shift:int, period:int = 1):
    #shift its a offset in minutes
    start_times = get_server_time(api) - (shift * 60000)
    historical_data = np.empty(shape=[0, 6])
    data_status = False
    while data_status == False:
        try:
            data = api.send_n_return(
                            {"command": "getChartLastRequest",
                            "arguments": {
                                "info": {
                                    "period": period,
                                    "start": start_times,
                                    "symbol": symbol
                                }
                            }
                        })
            print(data)
            candles_data = data["returnData"]["rateInfos"]
            for candle in candles_data:
                candle.pop("ctmString")
                candle_data = np.fromiter(
                    candle.values(), dtype=float
                ).reshape(1, 6)
                candle_data[0,2] = candle_data[0,1] + candle_data[0,2]
                candle_data[0,3] = candle_data[0,1] + candle_data[0,3]
                candle_data[0,4] = candle_data[0,1] + candle_data[0,4]
                historical_data = np.vstack([historical_data, candle_data])
            
            data_status = True
        except:
            sleep(2)
    return historical_data


def get_server_time(api):
    #1k to sekunda
    data = api.send_n_return({"command": "getServerTime"})
    print(data)
    return data["returnData"]["time"]



    
