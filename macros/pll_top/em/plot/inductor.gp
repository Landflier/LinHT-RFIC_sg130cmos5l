# SPDX-FileCopyrightText: 2026 Vasil Yordanov
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
#
# Plot differential L and Q vs frequency from an openEMS inductor sweep.
#
#   gnuplot -e "datafile='../results/<name>/<name>.csv'" inductor.gp
#
# Optional overrides:
#   -e "outfile='../results/foo.png'"   output file (default: alongside the CSV)
#   -e "ftank=2.45"                     marker frequency in GHz (default 2.45)
#   -e "fmax=15"                        x-axis limit in GHz (default: full sweep)
#
# CSV columns, written by models/run_inductor_diffport.py:
#   1:f_GHz  2:L_nH  3:Q  4:R_ohm  5:X_ohm

if (!exists("datafile")) {
    print "ERROR: pass the CSV, e.g. gnuplot -e \"datafile='x.csv'\" inductor.gp"
    exit
}
if (!exists("ftank"))   ftank = 2.45
if (!exists("outfile")) outfile = datafile[1:strlen(datafile)-4] . ".png"

set terminal pngcairo size 1000,700 enhanced font "Sans,11"
set output outfile

set multiplot layout 2,1 title sprintf("Differential inductor - %s", datafile) font "Sans,13"

set grid
set key top left
set xlabel "frequency [GHz]"
if (exists("fmax")) set xrange [0:fmax]

# marker at the tank frequency
set arrow 1 from ftank, graph 0 to ftank, graph 1 nohead lc rgb "#c00000" dt 2 lw 1.5
set label 1 sprintf("%.2f GHz", ftank) at ftank, graph 0.94 offset 1,0 tc rgb "#c00000"

set ylabel "L_{diff} [nH]"
set title "Inductance"
plot datafile using 1:2 with lines lw 2 lc rgb "#0060c0" notitle

set ylabel "Q_{diff}"
set title "Quality factor"
plot datafile using 1:3 with lines lw 2 lc rgb "#008040" notitle

unset multiplot
unset output
print "Wrote ", outfile
