v {xschem version=3.4.8RC file_version=1.3
*
* This file is part of XSCHEM,
* a schematic capture and Spice/Vhdl/Verilog netlisting tool for circuit
* simulation.
* Copyright (C) 1998-2024 Stefan Frederik Schippers
*
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation; either version 2 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 1240 -1000 2040 -600 {flags=graph
y1=-1.3
y2=1.3
ypos1=0.47116969
ypos2=0.71146047
divy=5
subdivy=1
unity=1
x1=-5e-08
x2=5e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
dataset=-1
unitx=1
logx=0
logy=0
color="4 7"
node="\\"up_dwn; up dwn -\\"
ref"
digital=0
rawfile=$netlist_dir/tran1.raw}
N 640 -610 660 -610 {lab=dwn}
N 640 -740 660 -740 {lab=up}
N 320 -740 340 -740 {lab=ref}
N 320 -580 340 -580 {lab=div}
N 490 -520 490 -500 {lab=VSS}
N 490 -820 490 -800 {lab=VDD1V2}
C {frame.sym} 0 0 0 0 {name=l1
author="Vasil Yordanov"
rev=1.0
title="untitled"
page=1
pages=1
description="A short description of the circuit"
lock=true}
C {simulator_commands.sym} 10 -130 0 0 {name=Libs_Xyce
simulator=xyce
only_toplevel=false
value="tcleval(
.lib $::SG13G2_MODELS_XYCE/cornerMOSlv.lib mos_tt
.lib $::SG13G2_MODELS_XYCE/cornerMOShv.lib mos_tt
.lib $::SG13G2_MODELS_XYCE/cornerRES.lib res_typ
.lib $::SG13G2_MODELS_XYCE/cornerDIO.lib dio_typ
)"}
C {simulator_commands.sym} 130 -130 0 0 {name=Libs_Vacask
simulator=vacask
only_toplevel=false
value="
include \\"sg13cmos5l_vacask_common.lib\\"
include \\"cornerMOSlv.lib\\" section=mos_tt
include \\"cornerMOShv.lib\\" section=mos_tt
include \\"cornerRES.lib\\" section=res_typ
include \\"cornerDIO.lib\\" section=dio_tt
include \\"sg13cmos5l_stdcell.inc\\"
"}
C {devices/launcher.sym} 1490 -215 0 0 {name=h3
descr="OP annotate"
tclcommand="xschem annotate_op"
}
C {devices/launcher.sym} 1490 -165 0 0 {name=h4
descr="Load waves"
tclcommand="
# VACASK names the raw file after the *analysis* (tran1), not the schematic
xschem raw_read $netlist_dir/tran1.raw tran
xschem setprop rect 2 0 fullxzoom
"
}
C {launcher.sym} 1490 -265 0 0 {name=h6
descr=SimulateXyce
tclcommand="
# Setup the default simulation commands if not already set up
# for example by already launched simulations.
set_sim_defaults

# Change the Xyce command. In the spice category there are currently
# 5 commands (0, 1, 2, 3, 4). Command 3 is the Xyce batch
# you can get the number by querying $sim(spice,n)
set sim(spice,3,cmd) \{Xyce -plugin $env(PDK_ROOT)/$env(PDK)/libs.tech/xyce/plugins/Xyce_Plugin_PSP103_VA.so \\"$N\\"\}

# change the simulator to be used (Xyce)
set sim(spice,default) 3

# Xyce uses the spice netlist format (update internal state, not just the Tcl var)
xschem set netlist_type spice

# run netlist and simulation
xschem netlist
simulate
"}
C {launcher.sym} 1490 -315 0 0 {name=h7
descr=SimulateVACASK
tclcommand="
# Setup the default simulation commands if not already set up
# for example by already launched simulations.
set_sim_defaults

# In the spectre netlist category, command #0 is VACASK. --extra-tomlfile adds
# the repo's SG13CMOS5L .vacaskrc.toml (include=ported models, module=PDK OSDI)
# so 'include sg13cmos5l_vacask_common.lib' resolves. LINHT_ROOT is exported by
# the xschemrc; PDK_ROOT comes from sak-pdk.
set sim(spectre,0,cmd) \{vacask --extra-tomlfile \\"$env(LINHT_ROOT)/models/vacask/ihp-sg13cmos5l/.vacaskrc.toml\\" \\"$N\\"\}
set sim(spectre,default) 0

# Switch the *internal* netlist type. simulate reads [xschem get netlist_type]
# (not the Tcl var), so 'set netlist_type' alone would netlist as spectre but
# still run ngspice. 'xschem set' updates both. NGSPICE/Xyce switch it back.
xschem set netlist_type spectre

# Create FET/BIP .save file for operating-point annotation
file mkdir $netlist_dir
write_data [save_params] $netlist_dir/[file rootname [file tail [xschem get current_name]]].save

# run netlist and simulation
xschem netlist
simulate
"}
C {simulator_commands.sym} 1230 -1150 0 0 {name=XYCE
simulator=xyce
only_toplevel=false
value="
.preprocess replaceground true
.option temp=27
.op
"}
C {simulator_commands.sym} 1350 -1150 0 0 {name=Script_VACASK
simulator=vacask
only_toplevel=false
value="
// PFD phase-detector characteristic: at fixed f_ref, sweep the div-clock
// delay offset phdel (= static phase error) and average UP/DWN over the
// steady-state tail. phase[deg] = 360*phdel/T -> -180..+180 deg.
// VACASK scoping (see .llm/vacask-simulation.md): netlist 'parameters' are
// NOT visible in control-block expressions, and an instance parameter bound
// to an expression cannot be swept. So all values are circuit variables
// ('var', control-block statement, visible everywhere) and the sweep steps
// the variable phdel instead of vdiv.delay directly.

model vsrc vsource
// supply rails driven from the TB 
vvdd (VDD1V2 0) vsrc dc=vdd
vss (VSS 0) vsrc dc=0
vref (ref 0) vsrc type=\\"pulse\\" val0=0 val1=vdd rise=tedge fall=tedge width=T/2 delay=phd period=T
vdiv (div 0) vsrc type=\\"pulse\\" val0=0 val1=vdd rise=tedge fall=tedge width=T/2 delay=phd+phdel period=T

control
  var vdd=1.2 fref=10e6 phdel=0
  var T=1/fref
  var tedge=T/1000
  var phd=2*T trun=4*T
  options temp=27 rawfile=\\"binary\\"
  save default
  // sweep the static phase offset across one full period -> (-180, +180] deg
  sweep ph variable=\\"phdel\\" from=-T/2 to=T/2 mode=\\"lin\\" points=41 continuation=0
  analysis tran1 tran stop=phd+trun step=tedge maxstep=T/500
endc
"}
C {pfd_top.sym} 490 -660 0 0 {name=x1}
C {lab_pin.sym} 320 -740 0 0 {name=pref sig_type=std_logic lab=ref}
C {lab_pin.sym} 660 -740 0 1 {name=pup sig_type=std_logic lab=up}
C {lab_pin.sym} 660 -610 0 1 {name=pdwn sig_type=std_logic lab=dwn}
C {lab_pin.sym} 320 -580 0 0 {name=pdiv sig_type=std_logic lab=div}
C {lab_pin.sym} 490 -500 1 1 {name=pvss sig_type=std_logic lab=VSS}
C {lab_pin.sym} 490 -820 3 1 {name=pvdd1 sig_type=std_logic lab=VDD1V2}
