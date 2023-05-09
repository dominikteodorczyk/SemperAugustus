from time import sleep
import logging

class Wallet():
    def __init__(self) -> None:
        self.testwallet = 1
        pass

    def run(self):
        while True:
            print('Wallet')
            self.testwallet += 1
            sleep(1)
