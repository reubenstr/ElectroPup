import numpy as np

class MovingAverage:
    def __init__(self, window_size):
        self.window_size = window_size
        self.data = []

    def add_data(self, new_value):
        self.data.append(new_value)
        if len(self.data) > self.window_size:
            self.data.pop(0)

    def moving_average(self):
        return np.mean(self.data)