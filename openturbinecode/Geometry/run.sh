#!/bin/bash

python AD2BB3D.py

mv data.dat Madsen_DTU10MW/

cd Madsen_DTU10MW

./make_blade

mv blade.igs ../
