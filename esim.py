import threading
import time
import numpy as np
import matplotlib.pyplot as plt

oja1 = np.zeros((100, 1))
oja2 = np.zeros((100, 1))
allas_iso = np.ones((60, 40))

tiedot ={}
tiedot["allas"] = allas_iso
tiedot["oja1"] = oja1

kuppila_semafori = threading.Semaphore(10)
kuppila_lukko = threading.Lock()

tiedot["istumapaikat_puhtaus"] = 10

def kayppa_vessassa():
    with kuppila_lukko:
        time.sleep(10)

def istuta_asiakas():
    global tiedot
    with kuppila_semafori:
        for i in range(10):
            print("Nyt ollaan kriittisellä alueella...")
            print("...koska paikkoja on vähän")
            tiedot["istumapaikat_puhtaus"] = tiedot["istumapaikat_puhtaus"] - 1
            time.sleep(1)
        
def kayppa_istumaan_saikeistin():
    kahva = threading.Thread(target=istuta_asiakas)
    kahva.start()

