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
N 470 -790 470 -750 {lab=VDD3V3}
N 430 -790 470 -790 {lab=VDD3V3}
N 470 -690 470 -640 {lab=#net1}
N 470 -550 470 -430 {lab=VBP}
N 510 -720 550 -720 {lab=VSS}
N 550 -610 550 -550 {lab=VBP}
N 510 -610 550 -610 {lab=VBP}
N 470 -550 550 -550 {lab=VBP}
N 470 -580 470 -550 {lab=VBP}
N 470 -370 470 -290 {lab=VSS3V3}
N 730 -720 770 -720 {lab=VSS}
N 690 -790 690 -750 {lab=VDD3V3}
N 650 -790 690 -790 {lab=VDD3V3}
N 730 -610 880 -610 {lab=VBP}
N 830 -720 870 -720 {lab=UP}
N 690 -690 690 -640 {lab=#net2}
N 910 -790 910 -750 {lab=VDD3V3}
N 690 -790 910 -790 {lab=VDD3V3}
N 920 -370 920 -290 {lab=VSS3V3}
N 690 -290 920 -290 {lab=VSS3V3}
N 690 -370 690 -290 {lab=VSS3V3}
N 650 -290 690 -290 {lab=VSS3V3}
N 690 -550 690 -530 {lab=VBN}
N 690 -550 770 -550 {lab=VBN}
N 690 -580 690 -550 {lab=VBN}
N 770 -550 770 -500 {lab=VBN}
N 730 -500 770 -500 {lab=VBN}
N 770 -500 880 -500 {lab=VBN}
N 920 -550 920 -530 {lab=VCTRL}
N 690 -470 690 -430 {lab=#net3}
N 920 -470 920 -430 {lab=#net4}
N 730 -400 770 -400 {lab=VDD3V3}
N 830 -400 880 -400 {lab=DN}
N 650 -610 690 -610 {lab=VDD3V3}
N 650 -720 650 -610 {lab=VDD3V3}
N 470 -790 650 -790 {lab=VDD3V3}
N 650 -720 690 -720 {lab=VDD3V3}
N 650 -790 650 -720 {lab=VDD3V3}
N 910 -720 950 -720 {lab=VDD3V3}
N 950 -720 950 -610 {lab=VDD3V3}
N 950 -790 950 -720 {lab=VDD3V3}
N 910 -790 950 -790 {lab=VDD3V3}
N 920 -610 950 -610 {lab=VDD3V3}
N 920 -500 960 -500 {lab=VSS3V3}
N 960 -400 960 -290 {lab=VSS3V3}
N 920 -290 960 -290 {lab=VSS3V3}
N 920 -400 960 -400 {lab=VSS3V3}
N 960 -500 960 -400 {lab=VSS3V3}
N 650 -500 690 -500 {lab=VSS3V3}
N 650 -400 650 -290 {lab=VSS3V3}
N 510 -290 650 -290 {lab=VSS3V3}
N 650 -400 690 -400 {lab=VSS3V3}
N 650 -500 650 -400 {lab=VSS3V3}
N 430 -720 470 -720 {lab=VDD3V3}
N 430 -790 430 -720 {lab=VDD3V3}
N 360 -790 430 -790 {lab=VDD3V3}
N 430 -720 430 -610 {lab=VDD3V3}
N 430 -610 470 -610 {lab=VDD3V3}
N 470 -400 510 -400 {lab=VSS3V3}
N 510 -400 510 -290 {lab=VSS3V3}
N 470 -290 510 -290 {lab=VSS3V3}
N 360 -290 470 -290 {lab=VSS3V3}
N 920 -550 1030 -550 {lab=VCTRL}
N 920 -580 920 -550 {lab=VCTRL}
N 950 -790 1030 -790 {lab=VDD3V3}
N 960 -290 1030 -290 {lab=VSS3V3}
N 360 -400 430 -400 {lab=VBIAS}
C {frame.sym} 0 0 0 0 {name=l1
author="Vasil Yordanov"
rev=1.0
title="Current_Pump"
page=1
pages=1
description="A source-switched charge pump, 
providing the control voltage for the VCO
in the PLL loop. Notes:
- cascoded nMOS current source to reduce channel 
length modulation and increase output impedence
-"
lock=true}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 900 -400 0 0 {name=MN4
l=0.45u
w=0.3u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 900 -500 0 0 {name=MN5
l=0.45u
w=0.3u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {iopin.sym} 360 -290 0 1 {name=p1 lab=VSS3V3}
C {iopin.sym} 360 -790 0 1 {name=p2 lab=VDD3V3}
C {ipin.sym} 360 -720 0 0 {name=p3 lab=UP}
C {ipin.sym} 360 -500 0 0 {name=p4 lab=DN}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 450 -400 0 0 {name=MN1
l=0.45u
w=0.3u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 490 -610 0 1 {name=MP1
l=0.4u
w=0.3u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 490 -720 0 1 {name=MP2
l=0.4u
w=0.3u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {lab_pin.sym} 550 -720 1 1 {name=p5 sig_type=std_logic lab=VSS}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 710 -720 0 1 {name=MP3
l=0.4u
w=0.3u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {lab_pin.sym} 770 -720 1 1 {name=p6 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 550 -610 0 1 {name=p7 sig_type=std_logic lab=VBP}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 710 -610 0 1 {name=MP4
l=0.4u
w=0.3u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 900 -610 0 0 {name=MP6
l=0.4u
w=0.3u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 890 -720 0 0 {name=MP5
l=0.4u
w=0.3u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {lab_pin.sym} 830 -610 0 0 {name=p9 sig_type=std_logic lab=VBP}
C {lab_pin.sym} 830 -720 0 0 {name=p8 sig_type=std_logic lab=UP}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 710 -500 0 1 {name=MN3
l=0.45u
w=0.3u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 710 -400 0 1 {name=MN2
l=0.45u
w=0.3u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {lab_pin.sym} 770 -400 1 0 {name=p10 sig_type=std_logic lab=VDD3V3}
C {lab_pin.sym} 830 -400 0 0 {name=p11 sig_type=std_logic lab=DN}
C {opin.sym} 1030 -550 0 0 {name=p12 lab=VCTRL}
C {lab_pin.sym} 830 -500 0 0 {name=p13 sig_type=std_logic lab=VBN}
C {ipin.sym} 360 -400 0 0 {name=p14 lab=VBIAS}
