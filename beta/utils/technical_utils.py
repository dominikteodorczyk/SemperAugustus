from time import sleep
import logging

class SessionTechnicalController():
    #TODO: zauważalny jest problem niepoprwnosci dziaalnia sesji po 23
    # dobrze było by monitorować co się dzieje i gdy zbyt dużo transakji 
    # jest zamykanych od razu przy zerowym odzewie serwera to zawiesić 
    # dany slot transakcyjny (symbol)
    def __init__(self, symbols) -> None:
        self.symbols = symbols
        self.testcontroler = 2
        pass

    def check_transaction_rupture(self):
        pass

    def valid_transaction_status(self):
        pass

    def run(self):
        pass


class AssetParametersObservetor():
    #TODO: clasa obiektów obserwujących dany walor pod katem jego parametrów technicznych takich jak spread itp
    pass