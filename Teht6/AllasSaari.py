import threading
import time
import tkinter as tk
import numpy as np
import random as r
import winsound

### Global variables ###
number_of_monkeys = 100
active_monkeys = []
ernesti = {"name": "ernesti", "monkeys": [], "location": (134, 109), "state": "idle"}
kernesti = {"name": "kernesti", "monkeys": [], "location": (166, 109), "state": "idle"}
is_logical = False
ernesti_marker = None
kernesti_marker = None
pool = None
ernesti_fetch_iteration = 0
kernesti_fetch_iteration = 0
e_ditch = np.ones((100, 1))
k_ditch = np.ones((100, 1))
e_ditch_y = 10
k_ditch_y = 110
ditch_ready = False
lock = threading.Lock()
semaphore = threading.Semaphore(11)

### Sounds ###
def dink():
    winsound.Beep(10000,50)

def fanfare_e():
    winsound.Beep(400,10000)

def fanfare_k():
    winsound.Beep(1000,10000) 

def splash():
    winsound.Beep(800, 100)   # Slightly lower pitch (800 Hz for 100 ms)
### Visuals ###

def create_island_with_pool(canvas):
    #global parameters
    global ernesti
    global kernesti
    global ernesti_marker
    global kernesti_marker
    global pool
    # create island and ocean shore
    canvas.create_rectangle(0, 0, 300, 240, fill="yellow")
    canvas.create_rectangle(0, 0, 300, 10, fill="blue")
    # create pool
    pool = canvas.create_rectangle(120, 110, 180, 130, fill="light grey", outline="light grey")
    # create ditch plans
    canvas.create_rectangle(135, 10, 135, 110, fill="black")
    canvas.create_rectangle(165, 10, 165, 110, fill="black")
    # create forest on island
    canvas.create_rectangle(85, 150, 215, 220, fill="green")
    # create location markers for ernesti and kernesti
    ernesti_marker = canvas.create_rectangle(
        ernesti["location"][0] - 2, ernesti["location"][1] - 2,
        ernesti["location"][0] + 2, ernesti["location"][1] + 2,
        fill="white"
    )
    kernesti_marker = canvas.create_rectangle(
        kernesti["location"][0] - 2, kernesti["location"][1] - 2,
        kernesti["location"][0] + 2, kernesti["location"][1] + 2,
        fill="dark grey"
    )
    return canvas

#buttons
def create_buttons(canvas):
    ernesti_gets_monkey = tk.Button(canvas, text="E fetch monkey", command=lambda: find_a_monkey(canvas, "ernesti"))
    ernesti_gets_monkey.pack()
    ernesti_gets_monkey.place(x=10, y=250)
    
    kernesti_gets_monkey = tk.Button(canvas, text="K fetch monkey", command=lambda: find_a_monkey(canvas, "kernesti"))
    kernesti_gets_monkey.pack()
    kernesti_gets_monkey.place(x=10, y=280)
    
    e_monkey_starts_digging = tk.Button(canvas, text="E monkey dig", command=lambda: let_monkey_dig(canvas, ernesti["monkeys"][0], ernesti["name"]))
    e_monkey_starts_digging.pack()
    e_monkey_starts_digging.place(x=110, y=250)
    
    e_get_10_monkeys = tk.Button(canvas, text="E fetch 10 monkeys", command=lambda: ernesti_find_many_monkeys(canvas, "ernesti"))
    e_get_10_monkeys.pack()
    e_get_10_monkeys.place(x=210, y=250)
    
    k_monkey_starts_digging = tk.Button(canvas, text="K monkey dig", command=lambda: let_monkey_dig(canvas, kernesti["monkeys"][0], kernesti["name"]))
    k_monkey_starts_digging.pack()
    k_monkey_starts_digging.place(x=110, y=280)
    
    k_get_10_monkeys = tk.Button(canvas, text="K fetch 10 monkeys", command=lambda: kernesti_find_many_monkeys(canvas, "kernesti"))
    k_get_10_monkeys.pack()
    k_get_10_monkeys.place(x=210, y=280)

    ernesti_gets_monkey_and_dig = tk.Button(canvas, text="E fetch to dig", command=lambda: go_get_a_monkey(canvas, "ernesti", True))
    ernesti_gets_monkey_and_dig.pack()
    ernesti_gets_monkey_and_dig.place(x=60, y=310)

    kernesti_gets_monkey_and_dig = tk.Button(canvas, text="K fetch to dig", command=lambda: go_get_a_monkey(canvas, "kernesti", True))
    kernesti_gets_monkey_and_dig.pack()
    kernesti_gets_monkey_and_dig.place(x=160, y=310)

    fill_ditch_button = tk.Button(canvas, text="Fill ditch", command=lambda: fill_ditch(canvas))
    fill_ditch_button.pack()
    fill_ditch_button.place(x=60, y=340)

    begin_the_race = tk.Button(canvas, text="Begin race", command=lambda: start_race(canvas))
    begin_the_race.pack()
    begin_the_race.place(x=160, y=340)


# movement of ernesti, kernesti and monkeys
def move_ernesti(canvas, dx:int=0, dy:int=0):
    global ernesti_marker
    canvas.move(ernesti_marker, dx, dy)
    canvas.update()

def move_kernesti(canvas, dx:int=0, dy:int=0):
    global kernesti_marker
    canvas.move(kernesti_marker, dx, dy)
    canvas.update()

def move_monkey(canvas, monkey_marker, dx:int=0, dy:int=0):
    canvas.move(monkey_marker, dx, dy)
    canvas.update()

### Actions ###

#movement logic
"""
The following functions move ernesti, kernesti and monkeys around the island.
The functions move each character one step at a time, and schedule the next step
to be taken after a short delay with the canvas.after() method.
I found this method with the help of Github Copilot, and chose to use it because
it solves the problem of blocking the GUI while the characters are moving.
The nested function move() is called recursively until the character reaches its destination.
"""
def send_ernesti_to_forest(canvas):
    global ernesti
    def move():
        if ernesti["location"][0] >=120:
            ernesti["location"] = (ernesti["location"][0]-1, ernesti["location"][1])
            move_ernesti(canvas, dx=-1, dy=0)
            canvas.after(50, move)  # Schedule the next move
        elif ernesti["location"][1] <= 150:
            ernesti["location"] = (ernesti["location"][0], ernesti["location"][1]+1)
            move_ernesti(canvas, dx=0, dy=1)
            canvas.after(50, move)  # Schedule the next move
        else:
            ernesti["state"] = "idle"
    ernesti["state"] = "moving"
    move()

def send_kernesti_to_forest(canvas):
    def move():
        if kernesti["location"][0] <=180:
            kernesti["location"] = (kernesti["location"][0]+1, kernesti["location"][1])
            move_kernesti(canvas, dx=1, dy=0)
            canvas.after(50, move)  # Schedule the next move
        elif kernesti["location"][1] <= 150:
            kernesti["location"] = (kernesti["location"][0], kernesti["location"][1]+1)
            move_kernesti(canvas, dx=0, dy=1)
            canvas.after(50, move)  # Schedule the next move
        else:
            kernesti["state"] = "idle"
    kernesti["state"] = "moving"
    move()

def send_ernesti_to_ditch(canvas, ditch_y:int):
    def move():
        if ernesti["location"][1] > ditch_y:
            ernesti["location"] = (ernesti["location"][0], ernesti["location"][1]-1)
            move_ernesti(canvas, dx=0, dy=-1)
            canvas.after(50, move)  # Schedule the next move
        elif ernesti["location"][0] < 135:
            ernesti["location"] = (ernesti["location"][0]+1, ernesti["location"][1])
            move_ernesti(canvas, dx=+1, dy=0)
            canvas.after(50, move)  # Schedule the next move
        else:
            ernesti["state"] = "idle"
    ernesti["state"] = "moving"
    move()

def send_kernesti_to_ditch(canvas, ditch_y:int):
    def move():
        if kernesti["location"][1] > ditch_y:
            kernesti["location"] = (kernesti["location"][0], kernesti["location"][1]-1)
            move_kernesti(canvas, dx=0, dy=-1)
            canvas.after(50, move)  # Schedule the next move
        elif kernesti["location"][0] > 165:
            kernesti["location"] = (kernesti["location"][0]-1, kernesti["location"][1])
            move_kernesti(canvas, dx=-1, dy=0)
            canvas.after(50, move)  # Schedule the next move
        else:
            kernesti["state"] = "idle"
    kernesti["state"] = "moving"
    move()

def send_monkey_to_ditch(canvas, monkey, ditch_y: int):
    def move():
        if monkey["location"][1] > ditch_y:
            monkey["location"] = (monkey["location"][0], monkey["location"][1] - 1)
            move_monkey(canvas, dx=0, dy=-1, monkey_marker=monkey["marker"])
            canvas.after(50, move)  # Schedule the next move
        elif monkey["location"][0] < 135:
            monkey["location"] = (monkey["location"][0] + 1, monkey["location"][1])
            move_monkey(canvas, dx=+1, dy=0, monkey_marker=monkey["marker"])
            canvas.after(50, move)  # Schedule the next move
        elif monkey["location"][0] > 165:
            monkey["location"] = (monkey["location"][0] - 1, monkey["location"][1])
            move_monkey(canvas, dx=-1, dy=0, monkey_marker=monkey["marker"])
            canvas.after(50, move)  # Schedule the next move
        else:
            monkey["state"] = "idle"

    monkey["state"] = "moving"
    move()


#commands
def find_a_monkey(canvas, fetcher="ernesti"):
    """
    This function's main purpose is to reset the global variable is_logical to False
    before calling go_get_a_monkey() with the given fetcher.
    """
    global is_logical
    is_logical = False
    go_get_a_monkey(canvas, fetcher)



def go_get_a_monkey(canvas,fetcher="ernesti", dig_too=False):
    global ernesti
    global kernesti
    global is_logical
    ditch_y: int = 110
    e_ditch_y_is_logical:int=10
    k_ditch_y_is_logical:int=119
    

    def delay_until_dig(canvas, monkey, fetcher):
        if monkey["state"] == "moving":
            time.sleep(0.05)
            threading.Thread(target=delay_until_dig, args=(canvas, monkey, fetcher)).start()
        else:
            threading.Thread(target=let_monkey_dig, args=(canvas, monkey, fetcher)).start()

    def fetch_monkey():
        nonlocal ditch_y 
        ditch_y = r.randint(10, 110)

        if fetcher == "ernesti":
            # wait for ernesti to stop moving
            while ernesti["state"] == "moving":
                time.sleep(0.1)
            monkey = assign_monkey(canvas, len(ernesti["monkeys"]), ernesti["name"])
            send_monkey_to_ditch(canvas, ditch_y=ditch_y, monkey=monkey)
            if not dig_too:
                send_ernesti_to_ditch(canvas, ditch_y)
        else:
            # wait for kernesti to stop moving
            while kernesti["state"] == "moving":
                time.sleep(0.1)
            monkey = assign_monkey(canvas, len(kernesti["monkeys"]), fetcher)
            send_monkey_to_ditch(canvas, ditch_y=ditch_y, monkey=monkey)
            if not dig_too:
                send_kernesti_to_ditch(canvas, ditch_y)
        if dig_too:
            delay_until_dig(canvas, monkey, fetcher)

    #fetch with logic
    def ernesti_fetch_monkey_is_logical():
        nonlocal ditch_y
        nonlocal e_ditch_y_is_logical
        global e_ditch_y
        global ernesti
        global ernesti_fetch_iteration
        global semaphore
        global lock
        monkey = None  # Initialize monkey to ensure it is always defined

        with semaphore:
            if ernesti_fetch_iteration == 0:
                with lock:
                    ditch_y = r.randint(10, 110)
                    e_ditch_y = ditch_y
                # wait for ernesti to stop moving
                while ernesti["state"] == "moving":
                    time.sleep(0.1)
                monkey = assign_monkey(canvas, len(ernesti["monkeys"]), ernesti["name"])
                send_monkey_to_ditch(canvas, ditch_y=ditch_y, monkey=monkey)
                # rest in else to avoid double fetch
            else:
                ditch_y = e_ditch_y
                if ernesti_fetch_iteration == 1 and ditch_y % 10 <= 1:
                    ernesti_fetch_iteration += 1
                # ernesti's dig spot logic
                e_ditch_y_is_logical = 10 * ernesti_fetch_iteration + ditch_y % 10
                if e_ditch_y_is_logical >= ditch_y:
                    e_ditch_y_is_logical += 10
                # last digging spot
                if e_ditch_y_is_logical > 109:
                    e_ditch_y_is_logical = 109

                monkey = assign_monkey(canvas, len(ernesti["monkeys"]), fetcher)
                send_monkey_to_ditch(canvas, ditch_y=e_ditch_y_is_logical, monkey=monkey)
            with lock:
                ernesti_fetch_iteration += 1
            if monkey is not None:
                delay_until_dig(canvas, monkey, fetcher)

    def kernesti_fetch_monkey_is_logical():
        nonlocal ditch_y
        nonlocal k_ditch_y_is_logical
        global k_ditch_y
        global kernesti
        global kernesti_fetch_iteration
        monkey = None

        if kernesti_fetch_iteration == 0:
            with lock:
                ditch_y = r.randint(10, 110)
                k_ditch_y = ditch_y
            # wait for kernesti to stop moving
            while kernesti["state"] == "moving":
                time.sleep(0.1)
            monkey = assign_monkey(canvas, len(kernesti["monkeys"]), fetcher)
            send_monkey_to_ditch(canvas, ditch_y=ditch_y, monkey=monkey)
        # rest in else to avoid double fetch
        else:
            # kernesti's dig spot logic
            with lock:
                k_ditch_y_is_logical -= kernesti_fetch_iteration * 10
                print(f"Kernesti's next dig spot is {k_ditch_y_is_logical} at iteration {kernesti_fetch_iteration}")
            # after passing first dig spot
            if k_ditch_y_is_logical <= k_ditch_y:
                with lock:
                    k_ditch_y_is_logical -= k_ditch_y % 10
                    print(f"Kernesti's next dig spot is actually {k_ditch_y_is_logical}")
            # last digging spot
            if k_ditch_y_is_logical <= 14:
                with lock:
                    k_ditch_y_is_logical = 14
                    print("No, actually it's 14")
        
            monkey = assign_monkey(canvas, len(kernesti["monkeys"]), fetcher)
            send_monkey_to_ditch(canvas, ditch_y=k_ditch_y_is_logical, monkey=monkey)
        kernesti_fetch_iteration += 1

        if monkey is not None:
            threading.Thread(target=delay_until_dig, args=(canvas, monkey, fetcher)).start()

    
    if fetcher == "ernesti":
        send_ernesti_to_forest(canvas)
    else:
        send_kernesti_to_forest(canvas)

    if is_logical:
        if fetcher == "ernesti":
            fetch_thread = threading.Thread(target=ernesti_fetch_monkey_is_logical)
        else:
            fetch_thread = threading.Thread(target=kernesti_fetch_monkey_is_logical)
    else:
        fetch_thread = threading.Thread(target=fetch_monkey)    
    fetch_thread.start()

def dig(canvas, monkey, digspot=109):
    dig_spot=digspot
    global e_ditch
    global k_ditch
    global ditch_ready
    global lock
    global semaphore
    monkey_x, monkey_y = monkey["location"]

    while monkey["state"] == "digging":
        time.sleep(2**monkey["tiredness"]) # digging takes time
        threading.Thread(target=dink).start()
        with lock:
            if monkey_x < 140:
                e_ditch[dig_spot, 0] -= 1
            else:
                k_ditch[dig_spot, 0] -= 1
        with semaphore:
            move_monkey(canvas,monkey["marker"],dy=-1)
        dig_spot -= 1
        monkey_y -= 1
        monkey["location"] = (monkey_x, monkey_y)
        with lock:
            canvas.create_rectangle(
                monkey_x, monkey_y, 
                monkey_x, monkey_y+1, 
                fill="light grey", outline="light grey"
                )
        if not ditch_ready:
            monkey["tiredness"] += 1 # monkey gets tired
        if not monkey["active"]:
                break
        if  dig_spot < 0 or ditch_ready:
            monkey["state"] = "idle"
    monkey["state"] = "idle"


def let_monkey_dig(canvas, monkey, fetcher="ernesti"):
    global ernesti
    global kernesti
    global lock

    dig_spot = monkey["location"][1] - 10
    monkey["state"] = "digging"
    # remove monkey from fetcher's list so other monkeys can be put to work
    if fetcher == ernesti["name"]:
        ernesti["monkeys"].remove(monkey)
    else:
        kernesti["monkeys"].remove(monkey)
        
    # ensure digging happens outside main thread to distribute workload
    threading.Thread(target=dig, args=(canvas,monkey,dig_spot)).start()



#creates a monkey and assigns it to fetcher
def assign_monkey(canvas, index, fetcher:str):
    global number_of_monkeys
    global active_monkeys
    monkey = {"active": True}
    monkey["name"] = fetcher + "'s monkey #" + str(index+1)
    if fetcher == ernesti["name"]:
        monkey["location"] = ernesti["location"]
    else:
        monkey["location"] = kernesti["location"]
    monkey["state"] = "idle"
    monkey["tiredness"] = 0
    monkey_marker = canvas.create_oval(
        monkey["location"][0]-2, monkey["location"][1]-1,
        monkey["location"][0]+2, monkey["location"][1]+1,
        fill="brown"
        )
    monkey["marker"] = monkey_marker
    number_of_monkeys -= 1
    if fetcher == ernesti["name"]:
        ernesti["monkeys"].append(monkey)
    else:
        kernesti["monkeys"].append(monkey)
    active_monkeys.append(monkey)
    canvas.update()
    return monkey


def stop_all_monkeys():
    global active_monkeys
    for monkey in active_monkeys:
        monkey["state"] = "idle"
        monkey["active"] = False
        canvas.delete(monkey["marker"])
    active_monkeys = []

def fill_ditch(canvas):
    global e_ditch
    global k_ditch
    global ditch_ready
    global number_of_monkeys
    global ernesti
    global kernesti
    # reset ernesti and kernesti
    move_ernesti(canvas, dx=134-ernesti["location"][0], dy=109-ernesti["location"][1])
    move_kernesti(canvas, dx=166-kernesti["location"][0], dy=109-kernesti["location"][1])
    ernesti["location"] = (134, 109)
    kernesti["location"] = (166, 109)
    # reset ditches
    e_ditch = np.ones((100, 1))
    k_ditch = np.ones((100, 1))
    ditch_ready = False
    canvas.create_rectangle(135, 10, 135, 110, fill="black")
    canvas.create_rectangle(165, 10, 165, 110, fill="black")
    # empty the pool
    canvas.create_rectangle(120, 110, 180, 130, fill="light grey", outline="light grey")
    # reset monkeys
    stop_all_monkeys()
    number_of_monkeys = 100
    canvas.update()


def ernesti_find_many_monkeys(canvas, fetcher="ernesti", rounds=11):
    global ernesti
    global is_logical
    is_logical = True
    
    def get_the_monkeys(canvas, fetcher):
        for i in range(rounds):
            if i<1:
                go_get_a_monkey(canvas, fetcher,True)
                while ernesti["state"] == "moving":
                    time.sleep(0.1)
            else:
                time.sleep(1)
                threading.Thread(target=go_get_a_monkey, args=(canvas, fetcher, True)).start()
        time.sleep(1)
        threading.Thread(target=reset_fetch_iteration).start()
    
    def reset_fetch_iteration():
        global ernesti_fetch_iteration
        global lock
        with lock:
            ernesti_fetch_iteration = 0
    
    # use threading to avoid blocking the GUI
    threading.Thread(target=get_the_monkeys, args=(canvas, fetcher)).start()

def kernesti_find_many_monkeys(canvas, fetcher="kernesti", rounds=11):
    global kernesti
    global is_logical
    is_logical = True
    
    def get_the_monkeys(canvas, fetcher):
        for i in range(rounds):
            if i<1:
                go_get_a_monkey(canvas, fetcher,True)
                while kernesti["state"] == "moving":
                    time.sleep(0.1)
            else:
                time.sleep(1)
                threading.Thread(target=go_get_a_monkey, args=(canvas, fetcher, True)).start()
        time.sleep(1)
        threading.Thread(target=reset_fetch_iteration).start()

    def reset_fetch_iteration():
        global kernesti_fetch_iteration
        global lock
        with lock:
            kernesti_fetch_iteration = 0
    
    # use threading to avoid blocking the GUI
    threading.Thread(target=get_the_monkeys, args=(canvas, fetcher)).start()

# let the game begin
def start_race(canvas):
    threading.Thread(target=ernesti_find_many_monkeys, args=(canvas,)).start()
    threading.Thread(target=kernesti_find_many_monkeys, args=(canvas,)).start()

#check for completion
def check_ditch_completion(canvas):
    global e_ditch
    global k_ditch
    global ditch_ready
    global lock

    if np.sum(e_ditch) <= 0:
        canvas.create_rectangle(120, 110, 180, 130, fill="blue", outline="blue")
        threading.Thread(target=fanfare_e).start()
        stop_all_monkeys()
        with lock:
            ditch_ready = True
    if np.sum(k_ditch) <= 0:
        canvas.create_rectangle(120, 110, 180, 130, fill="blue", outline="blue")
        threading.Thread(target=fanfare_k).start()
        stop_all_monkeys()
        with lock:
            ditch_ready = True
    canvas.update()
        
    
def check_flow_e(canvas):
    global lock
    global e_ditch
    e_first = 0
    e_last = 0
    e_fill = []
    while e_first < 99:
        for i in range(e_first,100):
            if i == 0:
                with lock:
                    if e_ditch[i] < 1:
                        e_fill.append(i)
                        e_last = i
                    else:
                        break
            else:
                with lock:
                    if e_ditch[i] < 1 and e_ditch[i-1] < 1:
                        e_fill.append(i)
                        e_last = i
                    else:
                        break
        if e_first != e_last:
            threading.Thread(target=splash).start()
            with lock:
                canvas.create_rectangle(135, 10+e_first, 135, 10+e_last, fill="blue", outline="blue")
            e_first = e_last
            e_fill = []
        time.sleep(0.1)
    threading.Thread(target=check_ditch_completion, args=(canvas,)).start()

    
    
def check_flow_k(canvas):
    global lock
    global k_ditch
    splash = False
    k_first = 0
    k_last = 0
    k_fill = []
    while k_first < 99:
        for i in range(k_first,100):
            if i == 0:
                if k_ditch[i] < 1:
                    k_fill.append(i)
                    k_last = i
                else:
                    break
            else:
                with lock:
                    if k_ditch[i] < 1 and k_ditch[i-1] < 1:
                        k_fill.append(i)
                        k_last = i
                    else:
                        break
        if k_first != k_last:
            if not splash:
                threading.Thread(target=splash).start()
                splash = True
            with lock:
                canvas.create_rectangle(165, 10, 165, 10+k_last, fill="blue", outline="blue")
            k_first = k_last
            k_fill = []
        else:
            splash = False
        time.sleep(0.1)
    threading.Thread(target=check_ditch_completion, args=(canvas,)).start()


# Sea flows into the ditches
def water_flow(canvas):
    threading.Thread(target=check_flow_e, args=(canvas,)).start()
    threading.Thread(target=check_flow_k, args=(canvas,)).start()



if __name__ == "__main__":
    root = tk.Tk()
    root.title("AllasSaari")
    canvas = tk.Canvas(root, width=340, height=380)
    canvas.pack()
    create_island_with_pool(canvas)
    create_buttons(canvas)
    threading.Thread(target=water_flow, args=(canvas,)).start()
    root.mainloop()
