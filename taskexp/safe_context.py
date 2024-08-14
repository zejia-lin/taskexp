import multiprocessing
import signal
import sys
import os
from functools import wraps
import time
import traceback
import types


def catch_sigint():
    queue = multiprocessing.Queue()
    process_running = multiprocessing.Event()
    
    def _ask_exit(frame):
        """This function runs in a separate process to ask the user if they want to exit."""
        sys.stdin = open("/dev/tty")  # Reopen stdin to interact with the terminal directly
        sys.stdout.write("\nDo you really want to exit? (y/n): ")
        response = sys.stdin.readline()
        if response.lower() == "y\n":
            exit(130)

    def _sigint_handler(sig, frame, queue, running):
        """Signal handler that spawns a process to ask the user if they want to exit."""
        if not running.is_set():
            running.set()
            proc = multiprocessing.Process(target=_ask_exit, args=(frame,))
            proc.start()
            proc.join()
            running.clear()
            if proc.exitcode != 0:
                raise KeyboardInterrupt
            proc.close()

    def handler(sig, frame):
        _sigint_handler(sig, frame, queue, process_running)

    signal.signal(signal.SIGINT, handler)


def catch_except(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("Traceback (most recent call last):")
            print("".join(traceback.format_stack()[:-2]), end="")
            print("".join(traceback.format_exception(e)[1:]))
    return wrapper


class _CatchExceptMetaClass(type):
    def __new__(cls, name, bases, dct):
        for attr_name, attr_value in dct.items():
            if isinstance(attr_value, types.FunctionType) and not (
                attr_name.startswith("__") and attr_name.endswith("__")
            ):
                print(f"Decorating {attr_name}")
                dct[attr_name] = catch_except(dct[attr_name])
        return super().__new__(cls, name, bases, dct)


class CatchExceptBase(metaclass=_CatchExceptMetaClass):
    pass
