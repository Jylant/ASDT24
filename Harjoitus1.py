import math
import numpy as np
import matplotlib.pyplot as plt
import time
import random
import winsound

grid = np.zeros((100, 100))
kuu = random.randint(0, 99)
grid[0][kuu] = 1
kuu_in_grid = {"location": [0, kuu]}
print("Kuu on sijainnissa: ", kuu_in_grid["location"])
Ernesti = {}
Kernesti = {}
Ernesti["location"] = [99, random.randint(0, 99)]
Kernesti["location"] = [99, random.randint(0, 99)]
print("Ernesti on sijainnissa: ", Ernesti["location"])
if Ernesti["location"] == Kernesti["location"]:
    Kernesti["location"] = [random.randint(0, 99), random.randint(0, 99)]
print("Kernesti on sijainnissa: ", Kernesti["location"])
grid[99][Ernesti["location"][1]]=2
grid[99][Kernesti["location"][1]]=3

def countdown(int: a= 10):
    for i in range(a):
        print(a-i,"...")
        time.sleep(1)
        winsound.Beep(500, 200)

def E_liikkuu():
    
