import threading
import time

thread_count = 0
lock = threading.Lock()

def thread_function():
    global thread_count
    with lock:
        thread_count += 1
    print("Thread count: ", thread_count)
    while True:
        time.sleep(1)
        

def create_threads():
    while True:
        thread = threading.Thread(target=thread_function)
        thread.start()
        time.sleep(0.1)  # Adjust the sleep time as needed

if __name__ == "__main__":
    create_threads()