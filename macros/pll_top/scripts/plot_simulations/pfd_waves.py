#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
#
# Extract one phase point of the VACASK PFD phase-sweep transient
# (testbenches/xschem/pdf_tb.sch) as a waveform table for the signal plot:
# time, ref, div, UP, DWN and the internal reset node RST (raw name 'x1:RST',
# labeled in schematic/xschem/pfd_top.sch).
#
# Run inside IIC-OSIC-TOOLS (VACASK's rawfile module is on PYTHONPATH):
#     python3 pfd_waves.py <path/to/tran1.raw> [phase_deg]  >  data/pfd_waves.dat
#
# phase_deg defaults to +90; the nearest swept point is used (its actual value
# is recorded in the table header).

import sys
import numpy as np
from rawfile import rawread

FREF = 10e6               # reference frequency [Hz], keep in sync with the TB
T    = 1.0 / FREF

SIGNALS = ('ref', 'div', 'up', 'dwn', 'x1:RST')


def main(path, phase_deg):
    raw  = rawread(path).get(sweeps=1)
    want = phase_deg / 360.0 * T
    g    = min(range(raw.sweepGroups),
               key=lambda i: abs(raw.sweepData(i)['ph'] - want))
    got  = 360.0 * raw.sweepData(g)['ph'] / T
    cols = [raw[g, 'time']] + [raw[g, n] for n in SIGNALS]
    np.savetxt(sys.stdout, np.column_stack(cols), fmt='%13.6g',
               header=f'phase_err = {got:+.1f} deg\n'
                      'time           ref           div           up'
                      '            dwn           rst')


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        sys.exit('usage: pfd_waves.py <tran1.raw> [phase_deg]')
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) == 3 else 90.0)
