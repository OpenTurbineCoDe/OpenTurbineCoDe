# -*- coding: utf-8 -*-

###
### This file is generated automatically by SALOME v8.3.0 with dump python functionality
###

import sys
import salome

salome.salome_init()
theStudy = salome.myStudy

import salome_notebook
notebook = salome_notebook.NoteBook(theStudy)
sys.path.insert( 0, r'/home/kz/Desktop/BB3D')

###
### GEOM component
###

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS


geompy = geomBuilder.New(theStudy)

O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
blade_igs_1 = geompy.ImportIGES("/home/kz/Desktop/BB3D/Demo/blade.igs", True)
[Face_1,Face_2,Face_3,Face_4] = geompy.ExtractShapes(blade_igs_1, geompy.ShapeType["FACE"], True)
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( blade_igs_1, 'blade.igs_1' )
geompy.addToStudyInFather( blade_igs_1, Face_1, 'Face_1' )
geompy.addToStudyInFather( blade_igs_1, Face_2, 'Face_2' )
geompy.addToStudyInFather( blade_igs_1, Face_3, 'Face_3' )
geompy.addToStudyInFather( blade_igs_1, Face_4, 'Face_4' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

meshName = "Mesh_Simple2.cgns"

smesh = smeshBuilder.New(theStudy)
Mesh_1 = smesh.Mesh(Face_1)
Regular_1D = Mesh_1.Segment()
Local_Length_1 = Regular_1D.LocalLength(0.1,None,1e-07)
Quadratic_Mesh_1 = Regular_1D.QuadraticMesh()
Quadrangle_2D = Mesh_1.Quadrangle(algo=smeshBuilder.QUADRANGLE)
Mesh_2 = smesh.Mesh(Face_2)
status = Mesh_2.AddHypothesis(Local_Length_1)
status = Mesh_2.AddHypothesis(Quadratic_Mesh_1)
Regular_1D_1 = Mesh_2.Segment()
Quadrangle_2D_1 = Mesh_2.Quadrangle(algo=smeshBuilder.QUADRANGLE)
Mesh_3 = smesh.Mesh(Face_3)
status = Mesh_3.AddHypothesis(Local_Length_1)
status = Mesh_3.AddHypothesis(Quadratic_Mesh_1)
Regular_1D_2 = Mesh_3.Segment()
Quadrangle_2D_2 = Mesh_3.Quadrangle(algo=smeshBuilder.QUADRANGLE)
Mesh_4 = smesh.Mesh(Face_4)
status = Mesh_4.AddHypothesis(Local_Length_1)
status = Mesh_4.AddHypothesis(Quadratic_Mesh_1)
Regular_1D_3 = Mesh_4.Segment()
Quadrangle_2D_3 = Mesh_4.Quadrangle(algo=smeshBuilder.QUADRANGLE)
isDone = Mesh_1.Compute()
isDone = Mesh_2.Compute()
isDone = Mesh_3.Compute()
isDone = Mesh_4.Compute()
try:
  Mesh_1.ExportCGNS( r'/home/kz/Desktop/BB3D/'+meshName, 1, Mesh_1)
  pass
except:
  print 'ExportCGNS() failed. Invalid file name?'
try:
  Mesh_2.ExportCGNS( r'/home/kz/Desktop/BB3D/'+meshName, 0, Mesh_2)
  pass
except:
  print 'ExportCGNS() failed. Invalid file name?'
try:
  Mesh_3.ExportCGNS( r'/home/kz/Desktop/BB3D/'+meshName, 0, Mesh_3)
  pass
except:
  print 'ExportCGNS() failed. Invalid file name?'
try:
  Mesh_4.ExportCGNS( r'/home/kz/Desktop/BB3D/'+meshName, 0, Mesh_4)
  pass
except:
  print 'ExportCGNS() failed. Invalid file name?'


## Set names of Mesh objects
smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')
smesh.SetName(Quadrangle_2D.GetAlgorithm(), 'Quadrangle_2D')
smesh.SetName(Quadratic_Mesh_1, 'Quadratic Mesh_1')
smesh.SetName(Local_Length_1, 'Local Length_1')
smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')
smesh.SetName(Mesh_3.GetMesh(), 'Mesh_3')
smesh.SetName(Mesh_2.GetMesh(), 'Mesh_2')
smesh.SetName(Mesh_4.GetMesh(), 'Mesh_4')


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser(True)
