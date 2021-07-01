"""
OpenTurbineCoDe aerodynamic wrapper

authors: everybody
"""

# ================================================
# External python imports
# ================================================

# import numpy as np


try:
    # EXTERNAL OPTIONAL DEPENDENCIES
    # import ...
    pass
except ImportError as err:
    _has_MODULE = False
else:
    _has_MODULE = True

"""
Definition of a decorator to be used on every function that requires the sprcific module
"""
def requires_MODULE(function):
    def check_requirement(*args,**kwargs):
        if not _has_MODULE:
            raise ImportError("MODULE is required to do this.")
        function(*args,*kwargs)
    return check_requirement


@requires_MODULE
def hello_from_sample():
    print("hello again")


@requires_MODULE
def new_function():
    print("hello2")