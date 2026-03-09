import numpy as np
from openfast_toolbox.io import FASTOutputFile
from pathlib import Path


class StructuralProcessing:
    def __init__(self):
        self.root_fxr_max = []
        self.root_fyr_max = []
        self.root_mxr_max = []
        self.root_myr_max = []
        self.tip_tdxr_max = []
        self.tip_tdyr_max = []

    def postprocess_beamdyn(self, workingmodel: Path):
        beam_out = FASTOutputFile(workingmodel.with_suffix(".out")).toDataFrame()
        beam_out_np = beam_out.to_numpy()
        beam_out_np = np.transpose(beam_out_np)

        # Extract maximum values from the BeamDyn output
        self.root_fxr_max.append(beam_out_np[1].max())
        self.root_fyr_max.append(beam_out_np[2].max())
        self.root_mxr_max.append(beam_out_np[3].max())
        self.root_myr_max.append(beam_out_np[4].max())
        self.tip_tdxr_max.append(beam_out_np[5].max())
        self.tip_tdyr_max.append(beam_out_np[6].max())
