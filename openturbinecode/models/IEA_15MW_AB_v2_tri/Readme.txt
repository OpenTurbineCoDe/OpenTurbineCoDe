How to generate AoA data and other data needed for the verification process of the IEA-15MW wind turbine

A. Setup parameters for load case L1.x (wind speed = xx m/s, pitch angle = yy deg, rotor speed = zz rpm, )
	1. Open Turbine_asBuilt_InflowFile.dat
           Edit HWindSpeed = xx m/s in line 13		
	2. Open Turbine_asBuilt_ElastoDyn.dat
	   Edit BlPitch(1) = yy deg in line 30 
	   Edit BlPitch(2) = yy deg in line 31 
	   Edit BlPitch(3) = yy deg in line 32
	   Edit RotSpeed = zz rpm in line 35

B. Setup outputs (to obtaint AoAs, iflow angles, induction factors a, a', wind velocities and other parameters at any node of the rotor blade in the OutListParameters.xlsx)
	1. Open OutListParameters.xlsx to check the corresponding names, for examples: 
	   B1N1Vindx = Axial induced wind velocity at Blade 1, Node 1
	   B2N4Vindy = Tangential induced wind velocity at Blade 2, Node 4
	   B3N6AxInd = Axial induction factor at Blade 3, Node 6
	   B2N9Alpha = Angle of attack at Blade 2, Node 9
	   B1N2Phi = Inflow angle at Blade 1, Node 2
	2. Open Turbine_asBuilt_AeroDyn15_LC1pX.dat
	   Edit OutList in line 75

C. Run the simulation in OpenFAST
	1. Change directory in Window command line to the executable folder of OpenFAST, e.g. E:\FOWT\OpenFAST\build
	2. Run openfast_x64.exe with input *.fast file, e.g. 
	   E:\FOWT\OpenFAST\build>openfast_x64.exe E:\FOWT\ROSCO\ROSCO_toolbox-main\Test_Cases\OpenFASTModel-20211026T100721Z-001\Turbine_asBuilt.fst
	3. All results can be read in Turbine_asBuilt.out
	