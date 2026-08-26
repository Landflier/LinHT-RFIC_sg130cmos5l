# SPDX-FileCopyrightText: 2026 TODO
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Plots for the pfd macro based on the VACASK phase-sweep TB
# (testbenches/xschem/pdf_tb.sch).
#
# Inputs are whitespace-separated tables produced from the VACASK raw file by
# the python reducers (VACASK has no ngspice-style `meas`, so the averaging /
# extraction math lives there — this script only draws the exported tables).
# From scripts/plot_simulations/:
#   python3 pfd_char.py  ../../schematic/xschem/simulations/tran1.raw    > data/pfd_char.dat
#   python3 pfd_waves.py ../../schematic/xschem/simulations/tran1.raw 90 > data/pfd_waves.dat
#   gnuplot plot_pfd.gp
# or from the macro root:
#   make sim-view-xschem CELL=pfd
#
# Renders SVG + PDF into figures/ (no interactive windows).

CHAR  = 'data/pfd_char.dat'
WAVES = 'data/pfd_waves.dat'
VDD   = 1.2

set grid back linetype -1 dashtype 3 linecolor rgb '#c0c0c0'

# ---------------------------------------------------------------- figure 1 --
# PFD characteristic: steady-state <UP>, <DWN>, <UP-DWN> vs static phase error
FIG = 'figures/pfd_char'
set key top left
set xlabel 'phase error (deg)'
set ylabel 'steady-state average (V)'
set xrange [-185:185]
set xtics 45
PLOT = "plot CHAR using 1:4 with linespoints pointtype 7 pointsize 0.4 linewidth 2 linecolor rgb '#0c5da5' title '<UP - DWN>', CHAR using 1:(VDD-$2-$3) with linespoints pointtype 6 pointsize 0.4 linewidth 2 linecolor rgb '#ff2c00' title '<(VDD-UP) - DWN>  (UP as active-low)', CHAR using 1:2 with lines dashtype 2 linecolor rgb '#00b945' title '<UP>', CHAR using 1:3 with lines dashtype 2 linecolor rgb '#ff9500' title '<DWN>', VDD*x/360 with lines dashtype 3 linecolor rgb '#474747' title 'ideal VDD {/Symbol \327 f}/360'"

set terminal svg size 900,620 dynamic background rgb 'white'
set output FIG.'.svg'
@PLOT

set terminal pdfcairo size 9,6.2
set output FIG.'.pdf'
@PLOT

# ---------------------------------------------------------------- figure 2 --
# Signal plot at one swept phase point: ref, div, UP, DWN and internal RST,
# stacked with a vertical offset per trace (logic-analyzer style)
FIG = 'figures/pfd_waves'
set key off
set title system("head -n 1 '".WAVES."' | sed 's/^# *//'") noenhanced
set xlabel 't ({/Symbol m}s)'
unset ylabel
OFF = 1.5
set xrange [*:*]
set xtics autofreq
set yrange [-0.3:7.5]
set ytics ('ref' 0.6, 'div' 2.1, 'up' 3.6, 'dwn' 5.1, 'rst' 6.6)
PLOT = "plot WAVES using ($1*1e6):($2) with lines linewidth 1.5 linecolor rgb '#0c5da5', WAVES using ($1*1e6):($3+OFF) with lines linewidth 1.5 linecolor rgb '#00b945', WAVES using ($1*1e6):($4+2*OFF) with lines linewidth 1.5 linecolor rgb '#ff9500', WAVES using ($1*1e6):($5+3*OFF) with lines linewidth 1.5 linecolor rgb '#ff2c00', WAVES using ($1*1e6):($6+4*OFF) with lines linewidth 1.5 linecolor rgb '#845b97'"

set terminal svg size 900,620 dynamic background rgb 'white'
set output FIG.'.svg'
@PLOT

set terminal pdfcairo size 9,6.2
set output FIG.'.pdf'
@PLOT

unset output
