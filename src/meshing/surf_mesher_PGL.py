
import numpy as np
import sys
import os

from PGL.components.blademesher import BladeMesher
from PGL.main.planform import read_blade_planform
from PGL.main.bezier import BezierCurve
from PGL.main.curve import SegmentedCurve, Curve

from PGL.main.domain import write_x2d

import utils.convert_fXYZ_to_uXYZ as conv



def generateSurfMesh(R0, R, path_to_case, planform_file, airfoil_list, blend_var, output_name):

    output_folder = path_to_case + os.sep + 'PGL'
    #TODO: check that this folder exists

    m = BladeMesher()

    # path to the planform
    
    m.planform_filename = path_to_case + os.sep + 'PGL' + os.sep + planform_file

    # =============== MESH PARAMETERS =====================================
    # hardcoded for now :-/

    # spanwise and chordwise number of vertices
    m.ni_span = 129
    m.ni_chord = 257

    # redistribute points chordwise
    m.redistribute_flag = True
    # number of points on blunt TE
    m.chord_nte = 9 #17
    # set min TE thickness (which will open TE using AirfoilShape.open_trailing_edge)
    # d.minTE = 0.0002

    # user defined cell size at LE
    # when left empty, ds will be determined based on
    # LE curvature
    # m.dist_LE = np.array([])

    # airfoil family - can also be supplied directly as arrays
    m.blend_var = blend_var

    af_list = []
    for af in airfoil_list:
        af_list.append( path_to_case + os.sep + 'PGL' + os.sep + af + '.dat' )

    m.base_airfoils_path = af_list
    m.surface_spline = 'cubic'

    # number of vertices and cell sizes in root region
    # m.root_type = 'cylinder'
    # m.ni_root = 8
    # m.s_root_start = 0.0
    # m.s_root_end = 0.065
    # m.ds_root_start = 0.008
    # m.ds_root_end = 0.005
    m.root_type = 'cap'
    m.ni_root = 8
    m.s_root_start = 0.0
    m.s_root_end = 0.03
    m.ds_root_start = 0.001
    m.ds_root_end = 0.004
    m.cap_cap_radius = .001
    m.cap_Fcap = 0.9
    m.cap_Fblend = 0.7


    # add additional dist points to e.g. refine the root
    # for placing VGs
    # self.pf_spline.add_dist_point(s, ds, index)

    # inputs to the tip component
    # note that most of these don't need to be changed
    m.ni_tip = 11
    m.s_tip_start = 0.99
    m.s_tip = 0.995
    m.ds_tip_start = 0.001
    m.ds_tip = 0.00005

    m.tip_fLE1 = .5  # Leading edge connector control in spanwise direction.
                    # pointy tip 0 <= fLE1 => 1 square tip.
    m.tip_fLE2 = .5  # Leading edge connector control in chordwise direction.
                    # pointy tip 0 <= fLE1 => 1 square tip.
    m.tip_fTE1 = .5  # Trailing edge connector control in spanwise direction.
                    # pointy tip 0 <= fLE1 => 1 square tip.
    m.tip_fTE2 = .5  # Trailing edge connector control in chordwise direction.
                    # pointy tip 0 <= fLE1 => 1 square tip.
    m.tip_fM1 = 1.   # Control of connector from mid-surface to tip.
                    # straight line 0 <= fM1 => orthogonal to starting point.
    m.tip_fM2 = 1.   # Control of connector from mid-surface to tip.
                    # straight line 0 <= fM2 => orthogonal to end point.
    m.tip_fM3 = .2   # Controls thickness of tip.
                    # 'Zero thickness 0 <= fM3 => 1 same thick as tip airfoil.

    m.tip_dist_cLE = 0.0001  # Cell size at tip leading edge starting point.
    m.tip_dist_cTE = 0.0001  # Cell size at tip trailing edge starting point.
    m.tip_dist_tip = 0.00025  # Cell size of LE and TE connectors at tip.
    m.tip_dist_mid0 = 0.00025  # Cell size of mid chord connector start.
    m.tip_dist_mid1 = 0.00004  # Cell size of mid chord connector at tip.

    m.tip_c0_angle = 40.  # Angle of connector from mid chord to LE/TE

    m.tip_nj_LE = 20   # Index along mid-airfoil connector used as starting point for tip connector


    # ===========================================================================================

    # generate the mesh
    m.update()

    # rotate domain with flow direction in the z+ direction and blade1 in y+ direction
    # m.domain.rotate_x(-90)
    # m.domain.rotate_y(180)
    m.domain.rotate_z(-90)

    # # copy blade 1 to blade 2 and 3 and rotate
    # m.domain.add_group('blade1', list(m.domain.blocks.keys()))
    # m.domain.rotate_z(-120, groups=['blade1'], copy=True)
    # m.domain.rotate_z(120, groups=['blade1'], copy=True)

    # We scale back to real size with the total radius
    m.domain.scale(R-R0)
    m.domain.translate_z(R0)

    # split blocks to cubes of size 33^3
    m.domain.split_blocks(33)

    # Write EllipSys3D ready surface mesh
    # write_x2d(m.domain)
    # Write Plot3D surface mesh (in real size, not PGL normalization)
    m.domain.write_plot3d(output_folder+os.sep+output_name+".xyz")

    # Convert file so that we can use it with PyHyp
    conv.convert_fXYZ_to_uXYZ(output_folder+os.sep+output_name+".xyz",output_folder+os.sep+output_name+".unf.xyz")


def writePGLinputs(turbine_data, path_to_case, planform_file):
    
    output_folder = path_to_case + os.sep + 'PGL'

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    #-loop over airfoils and write them-
    print( "List of airfoils that I should write: ")
    for af in turbine_data["airfoils"]:
        #write the file...
        #...
        print( af )


    #-retrieve planform data and write it-
    R = turbine_data["R"]
    R0 = turbine_data["R0"]

    r_coords = np.array(turbine_data["chord"]["grid"]) * (R-R0) + R0
    ze = np.zeros(np.size(r_coords))

    twist = np.array(turbine_data["twist"]["value"]) * 180. / np.pi
    chord = turbine_data["chord"]["value"]
    pitch_ax = turbine_data["pitch_axis"]["value"]
    
    #determine the relative thickness at every r_coords
    r_af = np.array(turbine_data["airfoil_position"]["grid"])
    th_af = np.zeros(np.size(r_af))
    i = 0
    for af in turbine_data["airfoil_position"]["labels"]:
        th_af[i] = turbine_data["airfoils"][af]["relative_thickness"]
        i+=1

    thickness = np.interp( np.array(turbine_data["chord"]["grid"]), r_af, th_af )
    

    fname = output_folder + os.sep + planform_file

    #TODO: check that all rows they are the same size    
    data = np.asarray([ ze, ze, r_coords, ze, ze, twist, chord, thickness, pitch_ax, ze ])
    data = np.transpose(data)
    np.savetxt(fname, data, delimiter=" ")



# local test function
if __name__ == "__main__":

    path_to_case = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + os.sep + 'models' + os.sep + 'DTU_10MW' + os.sep + 'Madsen2019'
    
    output_name = 'sample_mesh'

    R0 = 2.8
    R = 89.166
    planform_file = 'DTU_10MW_RWT_blade_axis_straight_fine.dat'
    blend_var = [0.241, 0.301, 0.36, 0.48, 1.0]
    airfoil_list = ['ffaw3241','ffaw3301','ffaw3360','ffaw3480','cylinder']

    #Call the function:
    generateSurfMesh(R0, R, path_to_case, planform_file, airfoil_list, blend_var, output_name)