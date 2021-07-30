class DataPoint:
    def __init__(self, frame):
        self.frame = frame
        self.datapoints = {}

    def add_datapoint(self, name, metric):
        self.datapoints[name] = metric