"""
Module containing commands to APIs used outside the data stream.
"""

import logging
from time import sleep
import numpy as np
from api.client import Client


def get_trades(client: Client, order_no: int = None) -> dict:
    """
    Retrieves trading data for a specific order number from the specified API.

    Args:
        client (Client): An object representing the API to use for retrieving the data.
        order_no (int): An optional integer representing the order number.

    Returns:
        A dictionary containing the trading data for the specified order,
        or None if no data was found.
    """
    message = {"command": "getTrades", "arguments": {"openedOnly": True}}
    data_recive = False
    while data_recive is False:
        sleep(1)
        try:
            response = client.send_n_return(message)
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
        except:
            pass


def get_margin(client: Client, symbol: str, volume: float) -> float:
    """
    Calculate the margin required for a given trading position.

    Args:
        client (object): The client object used for API communication.
        symbol (str): The symbol of the trading position.
        volume (float): The volume of the trading position.

    Returns:
        float: The margin required for the trading position.
    """
    message = {
        "command": "getMarginTrade",
        "arguments": {"symbol": symbol, "volume": volume},
    }
    response = client.send_n_return(message)
    return response["returnData"]["margin"]


def buy_transaction(client: Client, symbol: str, volume: float) -> dict:
    """
    Opens a buy transaction and returns the position information.

    Args:
        client (Client): An object representing the API used to execute the transaction.
        symbol (str): A string representing the symbol of the asset to be bought.
        volume (float): A float representing the volume of the asset to be bought.

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
    buy_response = client.send_n_return(
        {"command": "tradeTransaction", "arguments": buy_arguments}
    )
    margin = get_margin(client=client, symbol=symbol, volume=volume)
    try:
        order_no = buy_response["returnData"]["order"]
        transactions_data = get_trades(client=client, order_no=order_no)
        position = {
            "order_no": order_no,
            "margin": margin,
            "transactions_data": transactions_data,
        }
    except:
        logging.info(f"{symbol} buy Transaction failed")
    if (
        buy_response["status"] is True
        and transactions_data is not None
        and margin is not None
    ):
        logging.info(f"{symbol} buy transaction opened (order no: {order_no})")
        return {
            "order_no": order_no,
            "margin": margin,
            "transactions_data": transactions_data,
        }
    else:
        logging.info(f"{symbol} buy transaction failed")


def sell_transaction(client: Client, symbol: str, volume: float) -> dict:
    """
    Opens a sell transaction and returns the position information.

    Args:
        client (Client): An object representing the API used to execute the transaction.
        symbol (str): A string representing the symbol of the asset to be bought.
        volume (float): A float representing the volume of the asset to be bought.

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
    sell_response = client.send_n_return(
        {"command": "tradeTransaction", "arguments": sell_arguments}
    )
    margin = get_margin(client=client, symbol=symbol, volume=volume)
    try:
        order_no = sell_response["returnData"]["order"]
        transactions_data = get_trades(client=client, order_no=order_no)
        position = {
            "order_no": order_no,
            "margin": margin,
            "transactions_data": transactions_data,
        }
    except:
        logging.info(f"{symbol} sell Transaction failed")
    if sell_response["status"] and transactions_data:
        logging.info(f"{symbol} sell transaction opened (order no: {order_no})")
        return {
            "order_no": order_no,
            "margin": margin,
            "transactions_data": transactions_data,
        }
    else:
        logging.info(f"{symbol} sell transaction failed")


def close_position(
    client: Client, symbol: str, position: int, volume: float, cmd: int
) -> dict:
    """
    Close a trading position.

    Args:
        client (Client): The client object used for API communication.
        symbol (str): The symbol of the trading position to be closed.
        position (int): The position number to be closed.
        volume (float): The volume of the trading position to be closed.
        cmd (int): The command type of the trading position (buy/sell).

    Returns:
        dict: Information about the closed position, including order details and profit.
    """
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
    while close_status is False:
        close_response = client.send_n_return(
            {"command": "tradeTransaction", "arguments": close_arguments}
        )
        if close_response["status"] is True:
            close_status = True
            server_time = client.send_n_return({"command": "getServerTime"})[
                "returnData"
            ]["time"]
            data_recive = False

            while data_recive is False:
                sleep(1)
                try:
                    trades_stats = client.send_n_return(
                        {
                            "command": "getTradesHistory",
                            "arguments": {"end": 0, "start": server_time - 10000},
                        }
                    )
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
                                "close_price": trade["close_price"],
                                "close_time": trade["close_time"],
                            }
                except:
                    pass


def get_historical_candles(
    client, symbol: str, shift: int, period: int = 1
) -> np.ndarray:
    """
    Retrieve historical candle data for a specific symbol.

    Args:
        client: The client object used for API communication.
        symbol (str): The symbol for which to retrieve historical candle data.
        shift (int): The number of historical candles to retrieve.
        period (int, optional): The period of each candle in minutes. Defaults to 1.

    Returns:
        np.ndarray: An array containing the historical candle data.
    """
    # shift its a offset in minutes
    start_times = get_server_time(client) - (shift * 6e4)
    historical_data = np.empty(shape=[0, 6])
    data_status = False
    while data_status is False:
        try:
            data = client.send_n_return(
                {
                    "command": "getChartLastRequest",
                    "arguments": {
                        "info": {
                            "period": period,
                            "start": start_times,
                            "symbol": symbol,
                        }
                    },
                }
            )
            candles_data = data["returnData"]["rateInfos"]
            for candle in candles_data:
                candle.pop("ctmString")
                candle_data = np.fromiter(candle.values(), dtype=float).reshape(1, 6)
                candle_data[0, 2] = candle_data[0, 1] + candle_data[0, 2]
                candle_data[0, 3] = candle_data[0, 1] + candle_data[0, 3]
                candle_data[0, 4] = candle_data[0, 1] + candle_data[0, 4]
                historical_data = np.vstack([historical_data, candle_data])
            data_status = True
        except:
            sleep(2)
    return historical_data


def get_server_time(client: Client) -> int:
    """
    Retrieves the server time from the specified client.

    Args:
        client (Client): The client object used to communicate with the server.
    """
    data = client.send_n_return({"command": "getServerTime"})
    return data["returnData"]["time"]
