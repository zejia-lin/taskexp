from .task import Task, create_log_fd
from .subprocess_runner import SubprocessRunner
from .timer import Timer

__version__ = "0.1.0"

__all__ = [
    "Task",
    "create_log_fd",
    "SubprocessRunner",
    "Timer"
]


_global_timer_singleton = Timer()

def getTimer():
    return _global_timer_singleton