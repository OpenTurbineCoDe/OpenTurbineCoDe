import os
import openturbinecode.utils.io as io
from openturbinecode.configs.pathing import PROJECT_ROOT


class StructuralInput:
    """Verifies and sets the input parameters depending on the structural solver.
    There are two options for the structural solver:
        1. BeamDyn files
        2. Program generated files
    """
    def __init__(self, turb_data=None, models=None):
        self.turb_data = turb_data
        self.models = models
        self.path_to_root = PROJECT_ROOT

        # Preload default paths
        self.DTU10MWBeamDyn = PROJECT_ROOT / "structure" / "BeamDyn" / "DTU10MW" / "DTU10MW_driver.inp"
        self.DTU10MWTACS = PROJECT_ROOT / "controls" / "tacs_setup" / "DTU_10MW_RWT_blade3D_rotated_Single.bdf"
        self.NREL5MWBeamDyn = PROJECT_ROOT / "structure" / "BeamDyn" / "NREL5MW" / "NREL5MW_driver.inp"

        self.workingmodel = self.DTU10MWBeamDyn
        self.set_default_values()

    def set_default_values(self):
        # Load turbine data if not provided
        if not self.turb_data or not self.models:
            path_to_tmp = os.path.join(self.path_to_root, "models", "DTU_10MW", "Madsen2019")
            turb_yaml = os.path.join(path_to_tmp, "Madsen2019_10.yaml")
            self.turb_data = io.load_yaml(turb_yaml)

        # Set default parameters
        self.T = [42., 46., 40., 35., 28., 25., 18., 12., 10.]
        self.TipLoadxCV = 1.0
        self.TipLoadxL = 0.5
        self.TipLoadxU = 1.5
        self.DistrLoadxCV = 1.0
        self.TwstSclFCV = 1.0
        # More defaults can be added here as needed

    def set_path_to_case(self, path_to_case):
        self.path_to_case = path_to_case
