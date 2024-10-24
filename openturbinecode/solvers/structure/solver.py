import subprocess
from pathlib import Path
import openturbinecode.utils.utilities as ut
from openfast_toolbox.io import FASTInputFile


class StructuralSolver:
    def __init__(self, workingmodel):
        # Convert workingmodel to a Path object
        self.workingmodel = Path(workingmodel)

    def run_model_update_beamdyn(self, tip_load, distr_load, twist_scale):
        print("New design synthesis:", self.workingmodel)

        # Initialize FASTInputFile with Path
        beam_file = FASTInputFile(self.workingmodel)
        primary_path = self.workingmodel.parent / beam_file["InputFile"].strip('"')
        primary_file = FASTInputFile(primary_path)

        # Update the beam file
        beam_file["TipLoad(1)"] = tip_load
        beam_file["DistrLoad(1)"] = distr_load
        primary_file["MemberGeom"][:, 3] *= twist_scale

        # Write updates to files
        beam_file.write()
        primary_file.write()

    def local_run(self):
        conf = ut.read_config()
        bd_driver = conf["lofi"]["path_to_beamdyn"]

        # No need to change this, as subprocess works with strings
        subprocess.run([bd_driver, str(self.workingmodel)])

    def send_to_hpc(self, local_path, remote_user, remote_path):
        # Convert local_path to Path object
        local_path = Path(local_path)

        # Run SCP command
        subprocess.run(["scp", "-r", str(local_path), f"{remote_user}@{remote_user}:{remote_path}"])

        # Remove files matching pattern in workingmodel
        subprocess.run(["rm", "-r", str(self.workingmodel / "rpm*")])
