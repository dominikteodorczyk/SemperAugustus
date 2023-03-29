import logging


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

    response = api.send_n_return(message)
    for trade in response["returnData"]:
        if trade["order2"] == order_no:
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

    try:
        order_no = buy_response["returnData"]["order"]
        transactions_data = get_trades(api=api, order_no=order_no)
        position = {
            "order_no": order_no,
            "transactions_data": transactions_data,
        }
    except:
        logging.info(f"[{symbol} BUY] Transaction failed")
        return None

    if buy_response["status"] and transactions_data:
        position = {
            "order_no": order_no,
            "transactions_data": transactions_data,
        }
        logging.info(
            f"[{symbol} BUY] transaction opened (order no: {order_no})"
        )
        return position
    else:
        logging.info(f"[{symbol} BUY] transaction failed")
        return None


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

    try:
        order_no = sell_response["returnData"]["order"]
        transactions_data = get_trades(api=api, order_no=order_no)
        position = {
            "order_no": order_no,
            "transactions_data": transactions_data,
        }
    except:
        logging.info(f"[{symbol} SELL] Transaction failed")
        return None

    if sell_response["status"] and transactions_data:
        position = {
            "order_no": order_no,
            "transactions_data": transactions_data,
        }
        logging.info(
            f"[{symbol} SELL] transaction opened (order no: {order_no})"
        )
        return position
    else:
        logging.info(f"[{symbol} SELL] transaction failed")
        return None
