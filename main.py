from src.trading.broker import TradingSession

def main():
    # List of trading instruments to include in the session
    trading_instruments = ['EURUSD']  #'USDJPY','GBPUSD','US500','AUDUSD','USDCHF','USDCAD','GBPCHF'    
    session = TradingSession(trading_instruments)
    session.session_init()
   
if __name__ == '__main__':
    main()