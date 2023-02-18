import functools


class RetrievingTradingData():

    def __init__(self) -> None:
        pass


    def command_rtd(func): #wraper do wysyłki komend rtd 
        def wrapped(**kwargs):
            return func(**kwargs)


    def getallsymbols(self):
        packet = {
	        "command": "getAllSymbols"
        }
        return packet

    def getcalendar(self):
        packet = {
	    "command": "getCalendar"
        }
        return packet
    

    def getchartlastrequest(self, parameters:dict):
        packet = {
            "command": "getChartLastRequest",
            "arguments": parameters
            }
        return packet
    

    def getcalendar(self):
        packet = {
	    "command": "getCalendar"
        }
        return packet

    
    def getcalendar(self):
        packet = {
	    "command": "getCalendar"
        }
        return packet