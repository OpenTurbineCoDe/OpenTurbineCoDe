import numpy as np
import os
import csv

def OFparse(outfile,nodeR):
   # Reading the csv output
   ofh = open(outfile)

   data = []
   for row in csv.reader(ofh, delimiter='\t' ):
      if len(row)<=1:
         continue
      Ncol = len(row)
      data = np.append(data,row)
   ofh.close()

   data = np.resize(data,[int(len(data)/Ncol),Ncol])

   # Identifying the rows of interest
   i = 0
   ifN0 = np.nan
   ifT0 = np.nan
   iPwr = np.nan
   iThr = np.nan
   iTrq = np.nan
   for str in data[0,:]:
      if "B1N1Fn" in str:
         ifN0 = i
      elif "B1N1Ft" in str:
         ifT0 = i
      elif "RtAeroPwr" in str:
         iPwr = i
      elif "RtAeroFxh" in str:
         iThr = i
      elif "RtAeroMxh" in str:
         iTrq = i   
      i+=1
      
   nodeRht = np.zeros(len(nodeR)+2)
   nodeRht[1:-1] = nodeR
   nodeRht[-1] = 5.03 
   
   fN = np.zeros(len(nodeR)+2)
   fT = np.zeros(len(nodeR)+2)
   pwr = np.nan

   # Time averaging the results for each spanwise station
   for i in range(len(nodeR)):
      fN[i+1] = np.mean(data[2:-1,ifN0+i].astype(np.float))
      fT[i+1] = np.mean(data[2:-1,ifT0+i].astype(np.float))

   if not np.isnan(iPwr):
      pwr = np.mean(data[2:-1,iPwr].astype(np.float))

   # Rough estimates of the torque/thrust using
   if np.isnan(iThr):
      thrust = np.trapz(fN,nodeRht)
      print('WARNING: did not find thrust in OF outputs. Integrating the loads as an estimate.')
   else:
      thrust = np.mean(data[2:-1,iThr].astype(np.float))
      
   if np.isnan(iTrq):
      torque = np.trapz(fT*np.array(nodeRht),nodeRht)
      print('WARNING: did not find torque in OF outputs. Integrating the loads as an estimate.')
   else:
      torque = np.mean(data[2:-1,iTrq].astype(np.float))

   return thrust, torque, pwr


def UAEHparse(outfile):
      # Reading the csv output
      ofh = open(outfile)

      thrust = np.nan
      torque = np.nan
      pwr = np.nan
      for row in csv.reader(ofh, delimiter=',' ):
         if len(row)<=1:
            continue
         if row[0] == '815':
            thrust = float(row[10])
         if row[0] == '816':
            torque = float(row[10])
         if row[0] == '822':
            pwr = float(row[10])*1e3            
      ofh.close()

      return thrust,torque, pwr

def getLiftDistribution(testcase):
    dicty = {}
    f = open(testcase, 'r')
    lines = [line.rstrip('\n') for line in f]
    f.close()
    vars_slice = lines[1].replace('Variables = ', '').split('" "')
    #el_line = lines[3].replace('  ZONETYPE=FELINESEG', '') \
    #    .replace('Elements=         ', '').replace(' Nodes =         ', ''). \
    #    split()
    #nodes = int(el_line[1])
    nodes = int(lines[3].replace('I=   ', ''))

    print('found %i nodes in the file\n'%nodes)
    
    for i in range(len(vars_slice)):
        vars_slice[i] = vars_slice[i].replace('"', '')
    vars_slice[-1] = vars_slice[-1].rstrip(' ')
    
    for i in range(len(vars_slice)):
        dicty[vars_slice[i]] = []
        for j in range(nodes):
            dicty[vars_slice[i]].append(float(lines[5+j+(nodes*i)]))
    return dicty
