from functools import wraps


def decorator_enabler(func=None, *, default_enabled=True):
    """
    Decorator for decorators that allows enabling/disabling the decorator.
    
    Args:
        func (callable, optional): The decorator function to be wrapped.
        default_enabled (bool): The default enabled state of the decorator.
    """
    if func is None:
        return lambda f: decorator_enabler(f, default_enabled=default_enabled)

    def wrapper(*args, **kwargs):
        enable_flag = kwargs.pop('enable', default_enabled)
        if enable_flag:
            return func(*args, **kwargs)
        else:
            return args[0]
    return wrapper