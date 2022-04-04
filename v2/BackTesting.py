from datetime import datetime, timedelta

class BackTest():
    def __init__(self, start_time, end_time, frequency_in_seconds):
        self.start_time : datetime = start_time
        self.end_time : datetime = end_time
        self.frequency_in_seconds : datetime = frequency_in_seconds
        self.current_time = self.start_time

    def start(self):
        self.current_time = self.start_time
        while(self.current_time<self.end_time):
            yield self.current_time
            self.current_time += timedelta(seconds=self.frequency_in_seconds)