import signal
import sys
from functools import wraps
import traceback


def ask_exit():
    try:
        response = input("\nDo you really want to exit? (y/n): ")
    except EOFError:
        return False
    return response.lower() == "y"


def signal_handler(sig, frame):
    if ask_exit():
        print("Exiting...")
        sys.exit(127)
    else:
        print("Continuing...")


def nointerrupt(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        original_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal_handler)
        try:
            return func(*args, **kwargs)
        finally:
            signal.signal(signal.SIGINT, original_handler)
    return wrapper


def noexcept(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Exception occurred: {e}")
            print(traceback.format_exc())
    return wrapper


def catch_all(func):
    """Catch all exception and keyboard interrupt"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return noexcept(nointerrupt(func))(*args, **kwargs)
    return wrapper
