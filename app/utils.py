import time

def timer():
    t0 = time.time()
    def end():
        return round((time.time() - t0) * 1000, 2)
    return end
