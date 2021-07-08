# ================================================
# External python imports
# ================================================

import sys
import os
# import matplotlib.pyplot as plt
import numpy
import subprocess

class Aerostructural:
    def __init__(self, path_to_case, turb_data=None, models=None):

        self.turb_data = turb_data
        self.models = models
        self.path_to_case = path_to_case

        self.setDefaultValues()

    def setDefaultValues(self):

        # Initialization of attributes
        if self.turb_data and self.models:
            #use turbine data and model data passed as argument to initialize this object
            #... TODO
            pass
        else:
            pass  # add hardcoded default values

    # ==================== MODULE-SPECIFIC FUNCTIONS ==========================================