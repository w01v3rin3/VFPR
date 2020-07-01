# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 14:54:07 2020

@author: xs27
"""
##################################################################
# Generate Netlist for Xyce, using poles and residues from VF
#
# Using minimum extra branch/node realization
# Node ordering:
#     GND 0; source 1;
#     Extra nodes: 2 3 4...
###################################################################

import numpy as np

def R_pole(R,f,R_index,node_index):
    f.write('R'+str(R_index)+' 0 '+str(node_index)+' '+str(R)+'\n')
    
# reuse for both pole and poles: same nodes connection
def L_pole(L,f,L_index,node_index):
    f.write('L'+str(L_index)+' 1 '+str(node_index)+' '+str(L)+'\n')
    
# assume R on GND side, L on source side, with extra node in between
# r1 is the RC R, r2 is the RL R
def R_poles(r1,r2,f,R_index,node_index):
    # RC
    f.write('R'+str(R_index)+' 0 '+str(node_index+1)+' '+str(r1)+'\n')
    # RL
    f.write('R'+str(R_index+1)+' '+str(node_index)+' '+str(node_index+1)+' '+str(r2)+'\n')
    
def C_poles(C,f,C_index,node_index):
    f.write('C'+str(C_index)+' 0 '+str(node_index+1)+' '+str(C)+'\n')

# Read poles-residues file
pole_list = open('VF_MS200_pr.txt','r')
total_list = pole_list.readlines()
pole_list.close()
# Create Netlist file
tot_time = '2ms'
filename = 'MS200_S11_'+tot_time #+'_R--'
f = open(filename+'.cir','w')

# First line is used as title and automatically ignored by Xyce
f.write('Poles-Residues Circuit\n') 
f.write('*\n')

# Comments for netlist
f.write('* Netlist generated from MS200, using Poles-Residues\n')
f.write('*\n')

# specify the voltage source, Check if they have PRBS
f.write('*Voltage Sources\n')
# PAT(VHI VLO TDelay TR TF TSAMPLE DATA Repeat)
f.write('VIN 1 0 PAT(5 0 0 10n 10n 50n b001110011000111010011010100011111111001011111011011110010101111101101100000001100000001110010001011011110001110101011000010000101101011110010110010101111001110100110001010101101000101010000101100110010100111001001100010000111101110110000011111110100011111011000000011001111001000000100100100110101111000110000111011100110110101100001001011101110111011001011001110011111011111100000100101101000000000011001110100101111001101111000111111111111001101011010011111101100111011011011111111011011110011100010001100101000011010010001011100111001001101011111010100101101001101001100000111001010101010101011111010011011111010000010111111001110101000111000010010001010101001110000101110101101010111111110100110101101011101000111100111000110000100001010011001000100100101000010010001111010100010010110011010111101010111100000100010110111101100010011110100110101100010010001100111010100111110010000000110001011001010111010111111011111000110001000111001001010011100111001000011011010010111111001101011111011000001110101111011110100101100010010010110111010000110110101011001101010011001110011110111010111000010000100010001010001111111001101000111010000010111010100101111110000011001100001100001011000101100001001111111110000001100011000010010011100101111000001101110000111111110001010011100100011101001011110010010110011100100101101100010010001001011011110101100111010110010100010101100110110000011011010101001100010011100010010010111000000101001001000011011001010110001110101011100000110011010011100010010011001101111100111101001110010010101001011110001000100000010010100010100011110011100110110001010101001010011110000000110110110011110101010011010101111111101010010001110100111100000000010111011111000000001011111001110100001100011111001011111001010110000011010110100111001011010011100101010001100101111010101010101110011111100100100000010011010011010100010111110111001000101001001000010000100111000100110010010110001100010001111001011111001101011100001110101110010111001101110000101100110000011011100100101101011011110110000100101111100100001110110011100001111000000011101 0)\n')

# Simulation command for Xyce
f.write('*Analysis Command\n')
f.write('.TRAN 2ns '+tot_time+'\n')

# Output variable, look into how to find source current
f.write('*Output\n')
# .PRINT <print type> [FILE=<output filename>] 
# + [FORMAT=<STD|NOINDEX|PROBE|TECPLOT|RAW|CSV|GNUPLOT|SPLOT>] 
# + [WIDTH=<print field width>] 
# + [PRECISION=<floating point output precision>] 
# + [FILTER=<absolute value below which a number outputs as 0.0>] 
# + [DELIMITER=<TAB|COMMA>] [TIMESCALEFACTOR=<real scale factor>] 
# + [OUTPUT_SAMPLE_STATS=<boolean>] [OUTPUT_ALL_SAMPLES=<boolean>] 
# + <output variable> [output variable]*
f.write('.PRINT TRAN FILE='+filename+'.txt\n')
f.write('+ FORMAT=csv DELIMITER=TAB\n')
f.write('+ I(VIN)\n')
f.write('*\n')


# Write the Resistors 
f.write('*Resistors\n')
R_index = 1
node_index = 2
for line in total_list:
    PR = line.split()
    if 3 == np.size(PR):
        p = float(PR[0])
        r = float(PR[1])
        R_pole(-p/r,f,R_index,node_index)
        R_index += 1
        node_index += 1
    elif 6 == np.size(PR):
        Rp = float(PR[0])
        Ip = float(PR[1])
        Rr = float(PR[2])
        Ir = float(PR[3])
        R_poles(-(Rr/(Rr*Rp+Ir*Ip)+Ir*Ip/Rr**2),Ir*Ip/Rr**2,f,R_index,node_index)
        R_index += 2
        node_index += 2

# Write the Capacitors
f.write('*Capacitors\n')
C_index = 1
node_index = 2
for line in total_list:
    PR = line.split()
    if 3 == np.size(PR):
        node_index += 1
    #     C_pole(??,f,C_index)
    # elif 6 == np.size(PR):
    elif 6 == np.size(PR):
        Rp = float(PR[0])
        Ip = float(PR[1])
        Rr = float(PR[2])
        Ir = float(PR[3])
        C_poles(Rr**3/(Rr**3+Ir*Ip*(Ir*Ip+Rr*Rp)),f,C_index,node_index)
        # C_poles(0,f,C_index,node_index)
        C_index += 1
        node_index += 2

# Write the Inductors
f.write('*Inductors\n')
L_index = 1
node_index = 2
for line in total_list:
    PR = line.split()
    if 3 == np.size(PR):
        L_pole(1/float(PR[1]),f,L_index,node_index)
        # L_pole(0,f,L_index,node_index)
        L_index += 1
        node_index += 1
    elif 6 == np.size(PR):
        Rr = float(PR[2])
        L_pole(0.5/Rr,f,L_index,node_index)
        # L_pole(0,f,L_index,node_index)
        L_index += 1
        node_index += 2
    

# End the file and close        
f.write('*\n')
f.write('.End')
f.close()



