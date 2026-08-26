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
N 360 -640 360 -550 {lab=RST}
N 540 -510 650 -510 {lab=DWN}
N 650 -620 650 -510 {lab=DWN}
N 650 -620 740 -620 {lab=DWN}
N 540 -770 650 -770 {lab=#net1}
N 650 -770 650 -660 {lab=#net1}
N 540 -750 740 -750 {lab=UP}
N 320 -820 320 -750 {lab=VDD1V2}
N 320 -530 360 -530 {lab=VDD1V2}
N 320 -570 320 -530 {lab=VDD1V2}
N 260 -510 360 -510 {lab=F_DIV}
N 320 -750 360 -750 {lab=VDD1V2}
N 250 -770 360 -770 {lab=F_REF}
N 510 -640 530 -640 {lab=#net2}
N 360 -640 430 -640 {lab=RST}
N 360 -730 360 -640 {lab=RST}
C {frame.sym} 0 0 0 0 {name=l1
author="Vasil Yordanov"
rev=1.0
title="PDF"
page=1
pages=1
description="A Phase-Frequency Detector. The operation
of the circuit is the following: it compares the phase
of F_REF and F_DIV, causing UP/DWN to trigger
dependingon whether the F_DIV signal trails or
lags F_REF (at the frequency trying to lock)"
lock=true}
C {sg13cmos5l_nand2_1.sym} 590 -640 0 1 {name=X1 VDD=VDD1V2 VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_dfrbp_1.sym} 450 -750 0 0 {name=XREF VDD=VDD1V2 VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_dfrbp_1.sym} 450 -530 2 1 {name=XDIV VDD=VDD1V2 VSS=VSS prefix=sg13cmos5l_ }
C {lab_pin.sym} 320 -820 0 0 {name=p1 sig_type=std_logic lab=VDD1V2}
C {lab_pin.sym} 320 -570 0 0 {name=p2 sig_type=std_logic lab=VDD1V2}
C {iopin.sym} 260 -510 0 1 {name=p3 lab=F_DIV}
C {iopin.sym} 250 -770 0 1 {name=p4 lab=F_REF}
C {iopin.sym} 740 -750 0 0 {name=p5 lab=UP}
C {iopin.sym} 740 -620 0 0 {name=p6 lab=DWN
}
C {sg13cmos5l_buf_4.sym} 470 -640 0 1 {name=x4 VDD=VDD1V2 VSS=VSS prefix=sg13cmos5l_ }
C {iopin.sym} 300 -960 0 1 {name=p7 lab=VDD1V2}
C {iopin.sym} 300 -930 0 1 {name=p8 lab=VSS}
C {lab_pin.sym} 360 -670 0 0 {name=p9 sig_type=std_logic lab=RST}
