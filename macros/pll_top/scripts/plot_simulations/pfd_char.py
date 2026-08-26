#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
#
# Reduce the VACASK PFD phase-sweep transient to the phase-detector
# characteristic. Reads the swept tran raw file produced by
# testbenches/xschem/pdf_tb.sch (sweep 'ph' steps the circuit variable phdel
# = static delay offset of the div clock) and emits, per phase point, the
# steady-state time-averages <UP>, <DWN>, <UP-DWN>.
#
# The averaging math lives here (VACASK has no built-in average); gnuplot only
# draws the resulting table.
#
# Run inside IIC-OSIC-TOOLS (VACASK's rawfile module is on PYTHONPATH):
#     python3 pfd_char.py <path/to/tran1.raw>  >  data/pfd_char.dat
#     gnuplot plot_pfd.gp
#
# NOTE: FREF/PHD/NSETTLE below must match the 'var' values in Script_VACASK
# (pdf_tb.sch). Keep them in sync if you retune the testbench.

import sys
import numpy as np
from rawfile import rawread

trapz = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz

FREF    = 10e6            # reference frequency [Hz]
T       = 1.0 / FREF      # reference period [s]
PHD     = 2 * T           # common pulse start delay (var phd)
NSETTLE = 5               # ref cycles after PHD discarded before averaging;
                          # >= 4.5 (latest div edge starts at PHD + T/2) and
                          # integer so the window (tmeas0..stop) spans whole
                          # periods and the average has no partial-cycle bias


def main(path):
    raw    = rawread(path).get(sweeps=1)
    tmeas0 = PHD + NSETTLE * T
    rows   = []
    for g in range(raw.sweepGroups):
        t   = raw[g, 'time']
        sel = t >= tmeas0                       # steady-state tail
        win = t[sel][-1] - t[sel][0]
        aup = trapz(raw[g, 'up'][sel],  t[sel]) / win
        adn = trapz(raw[g, 'dwn'][sel], t[sel]) / win
        phase_deg = 360.0 * raw.sweepData(g)['ph'] / T
        rows.append((phase_deg, aup, adn, aup - adn))
    rows.sort()
    np.savetxt(sys.stdout, np.array(rows), fmt='%12.6g',
               header='phase_deg      avgUP        avgDWN       avgUP-DWN')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('usage: pfd_char.py <tran1.raw>')
    main(sys.argv[1])
