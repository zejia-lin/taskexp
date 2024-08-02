import time


class TimeRecord:
    def __init__(self, start: float, name=None):
        self.name = name or "unamed"
        self.start = start
        self.end: float = 0
        self.childs = []
        self.parent = None

    def stop(self, end: float):
        self.end = end

    def add(self, record):
        record.parent = self
        self.childs.append(record)

    def __str__(self) -> str:
        if len(self.childs) > 0:
            childs = f", {str(self.childs)}"
        else:
            childs = ""
        return f"('{self.name}'={self.duration:.3f}s{childs})"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def duration(self):
        return self.end - self.start


class Timer:
    def __init__(self):
        self.records = []
        self.runnings = []

    def start(self, name: str = None):
        cur = TimeRecord(start=time.time(), name=name)
        self.runnings.append(cur)
        if len(self.runnings) == 1:
            self.records.append(cur)
        else:
            self.runnings[0].add(cur)

    def stop(self):
        if len(self.runnings) == 0:
            raise RuntimeError("No timer is running.")
        self.runnings[-1].stop(time.time())
        self.runnings.pop()

    def __str__(self) -> str:
        ret = f"Timer<{hex(id(self))}> [\n"
        tab = "  "
        for node in self.records:
            ret += tab + str(node) + "\n"
        ret += "]"
        return ret
    
    def __repr__(self) -> str:
        return self.__str__()


if __name__ == "__main__":
    timer = Timer()
    timer.start("Outer")
    time.sleep(0.1)
    timer.start("Inner")
    time.sleep(0.2)
    timer.stop()
    timer.stop()
    timer.start("Another")
    time.sleep(0.5)
    timer.stop()
    print(timer)
