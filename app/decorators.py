"""Decorator functions"""
from threading import Thread


def async(original_function):
    def wrapper(*args, **kwargs):
        thr = Thread(target=original_function, args=args, kwargs=kwargs)
        thr.start()
    return wrapper
