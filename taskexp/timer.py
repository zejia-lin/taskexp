import time
import json


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
    
    def to_dict(self):
        return {
            "name": self.name,
            "start": self.start,
            "end": self.end,
            "duration": self.duration,
            "childs": [child.to_dict() for child in self.childs]
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def flatten(self):
        def flatten_obj(self):
            flat_list = [self]
            for child in self.childs:
                flat_list.extend(flatten_obj(child))
            return flat_list
        
        flat = flatten_obj(self)
        ret = []
        for obj in flat:
            ret.append({
                "name": obj.name,
                "start": obj.start,
                "end": obj.end,
                "duration": obj.duration
            })
        return ret


class Timer:
    def __init__(self):
        self.records = []
        self.runnings = []
        self.counter = 0

    def start(self, name: str = None):
        if name is None:
            name = f"#{self.counter}"
        self.counter += 1
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

    def to_json(self):
        return json.dumps([record.to_dict() for record in self.records], indent=2)

    def flatten(self):
        ret = []
        for record in self.records:
            ret.extend(record.flatten())
        return ret

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
    print(timer.to_json())
    print(timer.flatten())
    print(timer.records[0].to_json())
