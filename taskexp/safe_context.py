import signal
import time
import threading
from functools import wraps
import traceback
import sys

_exit_event = threading.Event()
_confirm_exit = threading.Event()

def _handle_interrupt(signum, frame):
    print("\nInterrupt received. Do you want to exit? (yes/no): ", end='', flush=True)
    _confirm_exit.set()

def _input_thread():
    while not _exit_event.is_set():
        if _confirm_exit.is_set():
            response = input()
            if response.lower() in ('yes'):
                print("Exiting program...")
                _exit_event.set()
            elif response.lower() in ('no'):
                print("Continuing program...")
            else:
                print("Please enter 'yes' or 'no': ", end='', flush=True)
            _confirm_exit.clear()

# Set up the signal handler
signal.signal(signal.SIGINT, _handle_interrupt)

# Start the input thread
threading.Thread(target=_input_thread, daemon=True).start()


def nointerrupt(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        while not _exit_event.is_set():
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                pass
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
