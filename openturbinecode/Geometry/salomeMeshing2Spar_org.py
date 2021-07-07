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
[Face_1,Face_2,Face_3,Face_4,Face_5,Face_6] = geompy.ExtractShapes(blade_igs_1, geompy.ShapeType["FACE"], True)
[Edge_5,Edge_6,Edge_7,Edge_8] = geompy.ExtractShapes(Face_3, geompy.ShapeType["EDGE"], True)
[Edge_1,Edge_2,Edge_3,Edge_4] = geompy.ExtractShapes(Face_4, geompy.ShapeType["EDGE"], True)
Face_2_vertex_4 = geompy.GetSubShape(Face_2, [4])
Edge_5_vertex_2 = geompy.GetSubShape(Edge_5, [2])
Edge_9 = geompy.MakeEdge(Face_2_vertex_4, Edge_5_vertex_2)
Face_6_vertex_9 = geompy.GetSubShape(Face_6, [9])
Face_5_vertex_4 = geompy.GetSubShape(Face_5, [4])
Edge_10 = geompy.MakeEdge(Face_6_vertex_9, Face_5_vertex_4)
Edge_2_vertex_3 = geompy.GetSubShape(Edge_2, [3])
Edge_6_vertex_2 = geompy.GetSubShape(Edge_6, [2])
Edge_11 = geompy.MakeEdge(Edge_2_vertex_3, Edge_6_vertex_2)
Edge_2_vertex_2 = geompy.GetSubShape(Edge_2, [2])
Edge_6_vertex_3 = geompy.GetSubShape(Edge_6, [3])
Edge_12 = geompy.MakeEdge(Edge_2_vertex_2, Edge_6_vertex_3)
Face_7 = geompy.MakeFaceWires([Edge_9, Edge_11, Edge_5, Edge_1], 1)
Face_8 = geompy.MakeFaceWires([Edge_10, Edge_12, Edge_8, Edge_4], 1)
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( blade_igs_1, 'blade.igs_1' )
geompy.addToStudyInFather( blade_igs_1, Face_1, 'Face_1' )
geompy.addToStudyInFather( blade_igs_1, Face_2, 'Face_2' )
geompy.addToStudyInFather( blade_igs_1, Face_3, 'Face_3' )
geompy.addToStudyInFather( blade_igs_1, Face_4, 'Face_4' )
geompy.addToStudyInFather( blade_igs_1, Face_5, 'Face_5' )
geompy.addToStudyInFather( blade_igs_1, Face_6, 'Face_6' )
geompy.addToStudyInFather( Face_4, Edge_1, 'Edge_1' )
geompy.addToStudyInFather( Face_4, Edge_2, 'Edge_2' )
geompy.addToStudyInFather( Face_4, Edge_3, 'Edge_3' )
geompy.addToStudyInFather( Face_4, Edge_4, 'Edge_4' )
geompy.addToStudyInFather( Face_3, Edge_5, 'Edge_5' )
geompy.addToStudyInFather( Face_3, Edge_6, 'Edge_6' )
geompy.addToStudyInFather( Face_3, Edge_7, 'Edge_7' )
geompy.addToStudyInFather( Face_3, Edge_8, 'Edge_8' )
geompy.addToStudyInFather( Face_2, Face_2_vertex_4, 'Face_2:vertex_4' )
geompy.addToStudyInFather( Edge_5, Edge_5_vertex_2, 'Edge_5:vertex_2' )
geompy.addToStudy( Edge_9, 'Edge_9' )
geompy.addToStudyInFather( Face_6, Face_6_vertex_9, 'Face_6:vertex_9' )
geompy.addToStudyInFather( Face_5, Face_5_vertex_4, 'Face_5:vertex_4' )
geompy.addToStudy( Edge_10, 'Edge_10' )
geompy.addToStudyInFather( Edge_2, Edge_2_vertex_3, 'Edge_2:vertex_3' )
geompy.addToStudyInFather( Edge_6, Edge_6_vertex_2, 'Edge_6:vertex_2' )
geompy.addToStudy( Edge_11, 'Edge_11' )
geompy.addToStudyInFather( Edge_2, Edge_2_vertex_2, 'Edge_2:vertex_2' )
geompy.addToStudyInFather( Edge_6, Edge_6_vertex_3, 'Edge_6:vertex_3' )
geompy.addToStudy( Edge_12, 'Edge_12' )
geompy.addToStudy( Face_7, 'Face_7' )
geompy.addToStudy( Face_8, 'Face_8' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New(theStudy)
Mesh_1 = smesh.Mesh(Face_1)
Regular_1D = Mesh_1.Segment()
Local_Length_1 = Regular_1D.LocalLength(????,None,1e-07)
Quadratic_Mesh_1 = Regular_1D.QuadraticMesh()
Quadrangle_2D = Mesh_1.Quadrangle(algo=smeshBuilder.QUADRANGLE)
isDone = Mesh_1.Compute()
Mesh_2 = smesh.Mesh(Face_2)
status = Mesh_2.AddHypothesis(Local_Length_1)
status = Mesh_2.AddHypothesis(Quadratic_Mesh_1)
Regular_1D_1 = Mesh_2.Segment()
Quadrangle_2D_1 = Mesh_2.Quadrangle(algo=smeshBuilder.QUADRANGLE)
isDone = Mesh_2.Compute()
Mesh_3 = smesh.Mesh(Face_3)
status = Mesh_3.AddHypothesis(Local_Length_1)
status = Mesh_3.AddHypothesis(Quadratic_Mesh_1)
Regular_1D_2 = Mesh_3.Segment()
Quadrangle_2D_2 = Mesh_3.Quadrangle(algo=smeshBuilder.QUADRANGLE)
isDone = Mesh_3.Compute()
Mesh_4 = smesh.Mesh(Face_4)
status = Mesh_4.AddHypothesis(Local_Length_1)
status = Mesh_4.AddHypothesis(Quadratic_Mesh_1)
Regular_1D_3 = Mesh_4.Segment()
Quadrangle_2D_3 = Mesh_4.Quadrangle(algo=smeshBuilder.QUADRANGLE)
isDone = Mesh_4.Compute()
Mesh_5 = smesh.Mesh(Face_5)
status = Mesh_5.AddHypothesis(Local_Length_1)
status = Mesh_5.AddHypothesis(Quadratic_Mesh_1)
Regular_1D_4 = Mesh_5.Segment()
Quadrangle_2D_4 = Mesh_5.Quadrangle(algo=smeshBuilder.QUADRANGLE)
isDone = Mesh_5.Compute()
Mesh_6 = smesh.Mesh(Face_6)
status = Mesh_6.AddHypothesis(Local_Length_1)
status = Mesh_6.AddHypothesis(Quadratic_Mesh_1)
Regular_1D_5 = Mesh_6.Segment()
Quadrangle_2D_5 = Mesh_6.Quadrangle(algo=smeshBuilder.QUADRANGLE)
isDone = Mesh_6.Compute()
Mesh_7 = smesh.Mesh(Face_7)
status = Mesh_7.AddHypothesis(Local_Length_1)
status = Mesh_7.AddHypothesis(Quadratic_Mesh_1)
Regular_1D_6 = Mesh_7.Segment()
Quadrangle_2D_6 = Mesh_7.Quadrangle(algo=smeshBuilder.QUADRANGLE)
isDone = Mesh_7.Compute()
Mesh_8 = smesh.Mesh(Face_8)
status = Mesh_8.AddHypothesis(Local_Length_1)
status = Mesh_8.AddHypothesis(Quadratic_Mesh_1)
Regular_1D_7 = Mesh_8.Segment()
Quadrangle_2D_7 = Mesh_8.Quadrangle(algo=smeshBuilder.QUADRANGLE)
isDone = Mesh_8.Compute()
try:
  Mesh_1.ExportCGNS( r'/home/kz/Desktop/BB3D/Mesh_Simple2.cgns', 1, Mesh_1)
  pass
except:
  print 'ExportCGNS() failed. Invalid file name?'
try:
  Mesh_2.ExportCGNS( r'/home/kz/Desktop/BB3D/Mesh_Simple2.cgns', 0, Mesh_2)
  pass
except:
  print 'ExportCGNS() failed. Invalid file name?'
try:
  Mesh_3.ExportCGNS( r'/home/kz/Desktop/BB3D/Mesh_Simple2.cgns', 0, Mesh_3)
  pass
except:
  print 'ExportCGNS() failed. Invalid file name?'
try:
  Mesh_4.ExportCGNS( r'/home/kz/Desktop/BB3D/Mesh_Simple2.cgns', 0, Mesh_4)
  pass
except:
  print 'ExportCGNS() failed. Invalid file name?'
try:
  Mesh_5.ExportCGNS( r'/home/kz/Desktop/BB3D/Mesh_Simple2.cgns', 0, Mesh_5)
  pass
except:
  print 'ExportCGNS() failed. Invalid file name?'
try:
  Mesh_6.ExportCGNS( r'/home/kz/Desktop/BB3D/Mesh_Simple2.cgns', 0, Mesh_6)
  pass
except:
  print 'ExportCGNS() failed. Invalid file name?'
try:
  Mesh_7.ExportCGNS( r'/home/kz/Desktop/BB3D/Mesh_Simple2.cgns', 0, Mesh_7)
  pass
except:
  print 'ExportCGNS() failed. Invalid file name?'
try:
  Mesh_8.ExportCGNS( r'/home/kz/Desktop/BB3D/Mesh_Simple2.cgns', 0, Mesh_8)
  pass
except:
  print 'ExportCGNS() failed. Invalid file name?'


## Set names of Mesh objects
smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')
smesh.SetName(Quadrangle_2D.GetAlgorithm(), 'Quadrangle_2D')
smesh.SetName(Local_Length_1, 'Local Length_1')
smesh.SetName(Quadratic_Mesh_1, 'Quadratic Mesh_1')
smesh.SetName(Mesh_5.GetMesh(), 'Mesh_5')
smesh.SetName(Mesh_4.GetMesh(), 'Mesh_4')
smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')
smesh.SetName(Mesh_3.GetMesh(), 'Mesh_3')
smesh.SetName(Mesh_2.GetMesh(), 'Mesh_2')
smesh.SetName(Mesh_6.GetMesh(), 'Mesh_6')
smesh.SetName(Mesh_7.GetMesh(), 'Mesh_7')
smesh.SetName(Mesh_8.GetMesh(), 'Mesh_8')


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser(True)
