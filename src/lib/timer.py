from threading import Timer, Event


class RepeatingTimer:
    def __init__(self, interval, f, *args, **kwargs):
        self.interval = interval
        self.f = f
        self.args = args
        self.kwargs = kwargs

        self.timer = None
        self.stop_events = Event()

    def callback(self):
        if not self.stop_events.is_set():
            self.f(*self.args, **self.kwargs)
            self.start()

    def cancel(self):
        self.timer.cancel()

    def start(self):
        self.timer = Timer(self.interval, self.callback)
        self.timer.start()

    def end(self):
        self.stop_events.set()
